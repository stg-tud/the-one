/*
 * Copyright 2010 Aalto University, ComNet
 * Released under GPLv3. See LICENSE.txt for details.
 */
package input;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.*;
import java.util.concurrent.LinkedBlockingQueue;

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
	private double lastTimeStamp = -1;
	double currentTimeStamp;
	String currentId;
	double currentX;
	double currentY;
	private String currentLine;
	private final double minTime;
	private final double maxTime;
	private final double minX;
	private final double maxX;
	private final double minY;
	private final double maxY;
	private boolean normalize;
	private final Queue<List<Tuple<String, Coord>>> movesBuffer;


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
		// read in the rest of the file and keep it in the movesBuffer

		ArrayList<Tuple<String, Coord>> currentTimeStampMoves = new ArrayList<>();
		movesBuffer = new LinkedBlockingQueue<>();

		// if movements file has no values except header we skip the rest of the constructor
		if (!scanner.hasNextLine()) {
			return;
		}

		while (scanner.hasNextLine()) {
			currentLine = scanner.nextLine();

			if (currentLine.trim().length() == 0 || currentLine.startsWith(COMMENT_PREFIX)) {
				continue; /* skip empty and comment lines */
			}
			Scanner lineScan = new Scanner(currentLine);
			parseLine(lineScan);

			// if the new line contains a new timestamp, add list of tuples for
			// previous timestamp to buffer
			if (lastTimeStamp != currentTimeStamp && !currentTimeStampMoves.isEmpty()) {
				movesBuffer.add(currentTimeStampMoves);
				currentTimeStampMoves.clear();
			}
			currentTimeStampMoves.add(new Tuple<>(currentId, new Coord(currentX, currentY)));
			lastTimeStamp = currentTimeStamp;
		}
		// ---------------------------------------------------------------------------------------------
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
	public List<Tuple<String, Coord>> readNextMovements() {
		if (!movesBuffer.isEmpty()) return movesBuffer.poll();
		return new ArrayList<>();
	}

	/**
	 * Returns the time stamp where the last moves read with
	 * {@link #readNextMovements()} belong to.
	 * @return The time stamp
	 */
	public double getLastTimeStamp() {
		return lastTimeStamp;
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
	 * @param lineScan Line from file to parse
	 */
	private void parseLine(Scanner lineScan) {
		try {
			currentTimeStamp = lineScan.nextDouble();
			currentId = lineScan.next();
			currentX = lineScan.nextDouble();
			currentY = lineScan.nextDouble();
		} catch (Exception e) {
			throw new SettingsError("Invalid line '" + currentLine + "'");
		} finally {
			lineScan.close();
		}

		if (normalize) {
			currentTimeStamp -= minTime;
			currentX -= minX;
			currentY -= minY;
		}

	}
}
