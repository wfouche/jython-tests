//DEPS org.jline:jline:3.30.4

import org.jline.reader.LineReader;
import org.jline.reader.LineReaderBuilder;
import org.jline.terminal.Terminal;
import org.jline.terminal.TerminalBuilder;
import java.io.IOException;
import java.lang.InterruptedException;
import org.jline.utils.NonBlocking;
import java.util.concurrent.TimeUnit;

void main() throws IOException, InterruptedException {
	int timeoutSeconds = 10; // seconds
	Terminal terminal = TerminalBuilder.builder()
			.system(true)
			.build();
	terminal.enterRawMode();
	var reader = terminal.reader();
	var _reader = org.jline.utils.NonBlocking.nonBlocking("jbang", reader);
	var writer = terminal.writer();
	int b;
	StringBuilder line = new StringBuilder();
	long endTimeNanos = System.nanoTime() + TimeUnit.SECONDS.toNanos(timeoutSeconds);
	do {
		b = _reader.peek(100);
		if (b >= 0) {
			b = _reader.read();
			if (b == 8 || b == 127) {
				writer.print('\b');
				writer.print(' ');
				writer.print('\b');
				if (line.length() > 0) {
					line.deleteCharAt(line.length() - 1);
				}
			} else {
				writer.print((char) b);
				if (b != 13) line.append((char) b);
			}
			writer.flush();
		} else {
			Thread.sleep(100);
		}
	} while (b != 13 && System.nanoTime() < endTimeNanos);
	boolean timedOut = (System.nanoTime() >= endTimeNanos);
	_reader.shutdown();
	//reader.close();
	//writer.flush();
	//writer.close();
	//terminal.close();
	IO.println("Timed out = " + timedOut);
	IO.println("Line length = " + line.length());
	IO.println("Line = " + line);
}
