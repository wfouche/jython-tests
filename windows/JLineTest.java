//DEPS org.jline:jline:3.30.4
//DEPS org.jline:jline-terminal-jansi:3.30.4

import org.jline.reader.LineReader;
import org.jline.reader.LineReaderBuilder;
import org.jline.terminal.Terminal;
import org.jline.terminal.TerminalBuilder;
import java.io.IOException;
import java.lang.InterruptedException;
import org.jline.utils.NonBlocking;
import java.util.concurrent.TimeUnit;

void main() throws IOException, InterruptedException {
	int EOF = -1;
	int ENTER = 13;
	int BACKSPACE1 = 8;
	int BACKSPACE2 = 127;
	int timeoutSeconds = 10; // seconds
	Terminal terminal = TerminalBuilder.builder()
			.jna(true)
			.system(true)
			.build();
	terminal.enterRawMode();
	var reader = terminal.reader();
	var _reader = org.jline.utils.NonBlocking.nonBlocking("jbang", reader);
	var writer = terminal.writer();
	StringBuilder line = new StringBuilder();
	boolean running; int b;
	long endTimeNanos = System.nanoTime() + TimeUnit.SECONDS.toNanos(timeoutSeconds);
	do {
		b = _reader.peek(100);
		if (b >= 0) {
			b = _reader.read();
			if (b == BACKSPACE1 || b == BACKSPACE2) {
				if (line.length() > 0) {
					writer.print('\b');
					writer.print(' ');
					writer.print('\b');
					line.deleteCharAt(line.length() - 1);
				}
			} else {
				writer.print((char) b);
				if (b != ENTER) {
					line.append((char) b);
				}
			}
			writer.flush();
		} else {
			Thread.sleep(100);
		}
		running = System.nanoTime() < endTimeNanos;
	} while (b != EOF && b != ENTER && running);

	boolean timedOut = !running;

	_reader.shutdown();

	IO.println("Timed out = " + timedOut);
	IO.println("Line length = " + line.length());
	IO.println("Line = " + line);
}