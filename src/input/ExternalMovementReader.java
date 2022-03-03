/*
 * Copyright 2010 Aalto University, ComNet
 * Released under GPLv3. See LICENSE.txt for details.
 */
package input;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.*;
import java.util.concurrent.*;

import util.Tuple;

import core.Coord;
import core.SettingsError;


/**
 * Reader for ExternalMovement movement model's time-location tuples.
 * <P>
 * First line of the file should be the offset header. Syntax of the header
 * should be:<BR>
 * <CODE>minTime maxTime minX maxX minY maxY minZ maxZ</CODE>
 * <BR>
 * Last two values (Z-axis) are ignored at the moment but can be present
 * in the file.
 * <P>
 * Following lines' syntax should be:<BR>
 * <CODE>time id xPos yPos</CODE><BR>
 * where <CODE>time</CODE> is the time when a node with <CODE>id</CODE> should
 * be at location <CODE>(xPos, yPos)</CODE>.
 * </P>
 * <P>
 * All lines must be sorted by time. Sampling interval (time difference between
 * two time instances) must be same for the whole file.
 * </P>
 */
public class ExternalMovementReader {
	/* Prefix for comment lines (lines starting with this are ignored) */
	public static final String COMMENT_PREFIX = "#";
	/* min and max size for buffer during ingestion phase */
	public static final int MIN_READ_AHEAD = 2000;
	public static final int MAX_READ_AHEAD = 20000;
	private double currentTimeStamp;
	private String currentLine;
	private final double minTime;
	private final double maxTime;
	private final double minX;
	private final double maxX;
	private final double minY;
	private final double maxY;
	private boolean normalize;
	// because we're reading in the complete data in the constructor, lastTimeStamp can no
	// longer be used to fetch the current state of the read-in process. We store the
	// timestamp in the movesBuffer along with the associated data:
	// movesBuffer structure: (timestamp, [(node_id1, coord1), (node_id2, coord2), ...])
	private final BlockingQueue<Tuple<Double, List<Tuple<String, Coord>>>> movesBuffer;
	private CountDownLatch readPossible;
	private boolean enableCountDownLatch = false;
	private double lastReturnedTimestamp = -1;
	private boolean ingestDone = false;

	/**
	 * Constructor. Creates a new reader that reads the data from a file.
	 * @param inFilePath Path to the file where the data is read
	 * @throws SettingsError if the file wasn't found
	 */
	public ExternalMovementReader(String inFilePath) {
		this.normalize = true;
		File inFile = new File(inFilePath);
		Scanner scanner;
		try {
			scanner = new Scanner(inFile);
		} catch (FileNotFoundException e) {
			throw new SettingsError("Couldn't find external movement input " +
					"file " + inFile);
		}

		String offsets = scanner.nextLine();

		// read in the first line which contains min and max values for time, x, and y
		try (Scanner lineScan = new Scanner(offsets)) {
			minTime = lineScan.nextDouble();
			maxTime = lineScan.nextDouble();
			minX = lineScan.nextDouble();
			maxX = lineScan.nextDouble();
			minY = lineScan.nextDouble();
			maxY = lineScan.nextDouble();
		} catch (Exception e) {
			throw new SettingsError("Invalid offset line '" + offsets + "'");
		}

		// ---------------------------------------------------------------------------------------------
		// read in the rest of the file and push it into the movesBuffer
		System.out.println("Reading in " + inFilePath);
		movesBuffer = new LinkedBlockingQueue<>();
		currentTimeStamp = -1;
		Executors.newSingleThreadExecutor().submit(() -> readInFile(scanner));

		// ---------------------------------------------------------------------------------------------
	}


	private void readInFile(Scanner scanner) {
		ArrayList<Tuple<String, Coord>> currentTimeStampMoves = new ArrayList<>();

		// read in first line and set up timestamp variables
		if (!scanner.hasNextLine()) {
			ingestDone = true;
			return; /* if movements file has no values except header we're done*/
		}
		currentLine = scanner.nextLine();
		while (emptyOrCommentedOutLine(currentLine)) {
			currentLine = scanner.nextLine();
		};
		currentTimeStampMoves.add(parseLine(currentLine));
		double lastTimeStamp = currentTimeStamp;

		while (scanner.hasNextLine()) {
			// manage countdown to ensure we're in the accepted buffer size range
			if (movesBuffer.size() >= MAX_READ_AHEAD) {
				readPossible = new CountDownLatch(MAX_READ_AHEAD-MIN_READ_AHEAD);
				enableCountDownLatch = true;
				try {
					readPossible.await();
				} catch (InterruptedException e) {
					System.out.println("ERROR: Data ingestion interrupted.");
					e.printStackTrace();
				}
			}
			currentLine = scanner.nextLine();

			if (emptyOrCommentedOutLine(currentLine)) {
				continue; /* skip empty and comment lines */
			}

			lastTimeStamp = currentTimeStamp;
			// parseLine updates currentTimeStamp hooray for side-effects
			Tuple<String, Coord> currentTuple = parseLine(currentLine);

			// if the new line contains a new timestamp, add list of tuples for
			// previous timestamp to buffer
			if (lastTimeStamp != currentTimeStamp && !currentTimeStampMoves.isEmpty()) {
				movesBuffer.add(new Tuple<>(lastTimeStamp, currentTimeStampMoves));
				currentTimeStampMoves = new ArrayList<>();
			}
			currentTimeStampMoves.add(currentTuple);
		}
		// add last timestamp readings
		if (!currentTimeStampMoves.isEmpty()) {
			movesBuffer.add(new Tuple<>(lastTimeStamp, currentTimeStampMoves));
		}
		// set the flag to let readNextMovements-thread know we're done
		ingestDone = true;
	}

	private boolean emptyOrCommentedOutLine(String line) {
		return line.trim().length() == 0 || line.startsWith(COMMENT_PREFIX);
	}

	/**
	 * Sets normalizing of read values on/off. If on, values returned by
	 * {@link #readNextMovements()} are decremented by minimum values of the
	 * offsets. Default is on (normalize).
	 * @param normalize If true, normalizing is on (false -> off).
	 */
	public void setNormalize(boolean normalize) {
		this.normalize = normalize;
	}

	/**
	 * Reads all new id-coordinate tuples that belong to the same time instance
	 * @return A list of tuples or empty list if there were no more moves
	 */
	public synchronized List<Tuple<String, Coord>> readNextMovements() {
		Tuple<Double, List<Tuple<String, Coord>>> nextMove = null;
		try {
			// poll the buffer until an element becomes available
			while((nextMove = movesBuffer.poll(50L, TimeUnit.MILLISECONDS)) == null) {
				if (ingestDone) break;
			};
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
		if (enableCountDownLatch)
			readPossible.countDown();
		if (nextMove != null) {
			lastReturnedTimestamp = nextMove.getKey();
			return nextMove.getValue();
		}
		return new ArrayList<>();
	}

	/**
	 * Returns the time stamp where the last moves read with
	 * {@link #readNextMovements()} belong to.
	 * @return The time stamp
	 */
	public double getLastTimeStamp() {
		return lastReturnedTimestamp;
	}

	/**
	 * Returns offset maxTime
	 * @return the maxTime
	 */
	public double getMaxTime() {
		return maxTime;
	}

	/**
	 * Returns offset maxX
	 * @return the maxX
	 */
	public double getMaxX() {
		return maxX;
	}

	/**
	 * Returns offset maxY
	 * @return the maxY
	 */
	public double getMaxY() {
		return maxY;
	}

	/**
	 * Returns offset minTime
	 * @return the minTime
	 */
	public double getMinTime() {
		return minTime;
	}

	/**
	 * Returns offset minX
	 * @return the minX
	 */
	public double getMinX() {
		return minX;
	}

	/**
	 * Returns offset minY
	 * @return the minY
	 */
	public double getMinY() {
		return minY;
	}

	/**
	 * Parses the values of lineScan and writes them into the correpsonding o
	 * @param line Line from file to parse
	 * @return tuple of node movement
	 */
	private Tuple<String, Coord> parseLine(String line) {
		String[] splitLine = line.split(" ");
		if (splitLine.length != 4) throw new SettingsError("Invalid line '" + currentLine + "'");
		currentTimeStamp = Double.parseDouble(splitLine[0]);
		String id = splitLine[1];
		double x = Double.parseDouble(splitLine[2]);
		double y = Double.parseDouble(splitLine[3]);
		if (normalize) {
			currentTimeStamp -= minTime;
			x -= minX;
			y -= minY;
		}
		return new Tuple<>(id, new Coord(x, y));
	}
}
