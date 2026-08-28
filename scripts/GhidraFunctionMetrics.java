import ghidra.app.script.GhidraScript;
import ghidra.program.model.block.BasicBlockModel;
import ghidra.program.model.block.CodeBlock;
import ghidra.program.model.block.CodeBlockIterator;
import ghidra.program.model.block.CodeBlockReferenceIterator;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.InstructionIterator;

public class GhidraFunctionMetrics extends GhidraScript {
    @Override
    public void run() throws Exception {
        int functions = 0;
        int basicBlocks = 0;
        int edges = 0;
        int instructions = 0;
        BasicBlockModel blockModel = new BasicBlockModel(currentProgram);
        FunctionIterator functionIterator = currentProgram.getFunctionManager().getFunctions(true);
        while (functionIterator.hasNext() && !monitor.isCancelled()) {
            Function function = functionIterator.next();
            functions++;

            InstructionIterator instructionIterator = currentProgram.getListing()
                    .getInstructions(function.getBody(), true);
            while (instructionIterator.hasNext()) {
                instructionIterator.next();
                instructions++;
            }

            CodeBlockIterator blockIterator = blockModel.getCodeBlocks(monitor);
            while (blockIterator.hasNext()) {
                CodeBlock block = blockIterator.next();
                if (!function.getBody().contains(block.getFirstStartAddress())) {
                    continue;
                }
                basicBlocks++;
                CodeBlockReferenceIterator destinationIterator = block.getDestinations(monitor);
                while (destinationIterator.hasNext()) {
                    destinationIterator.next();
                    edges++;
                }
            }
        }

        println("R2MORPH_METRICS {\"functions\":" + functions
                + ",\"basic_blocks\":" + basicBlocks
                + ",\"edges\":" + edges
                + ",\"instructions\":" + instructions + "}");
    }
}
