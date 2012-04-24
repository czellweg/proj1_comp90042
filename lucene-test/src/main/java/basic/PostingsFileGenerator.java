package basic;

import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.apache.log4j.Logger;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.index.IndexWriterConfig.OpenMode;
import org.apache.lucene.index.Term;
import org.apache.lucene.index.TermDocs;
import org.apache.lucene.index.TermEnum;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.util.Version;

/**
 * Creates a postings file based on a Lucene-index. The format of the postings-file is 
 * 
 * This class has been copied from:
 * http://www.lucenetutorial.com/sample-apps/textfileindexer-java.html Several
 * changes have been made to fit my use case.
 */

public class PostingsFileGenerator {

    private static final Logger log = Logger.getLogger(PostingsFileGenerator.class);

    private IndexWriter writer;
    private List<File> queue = new ArrayList<File>();

    public static void main(String[] args) throws IOException {

        if (args.length != 2) {
            System.out.println("Usage: java -jar PFG.jar <path to indexdir> <path to dir to be indexed>");
            System.out.println("-------------------------------------------");
            System.out.println("Please provide the index directory to store " +
            		"the lucene index in and the directory which is to be indexed.");
            System.exit(-1);
        }
        
        String indexDir = args[0];
        PostingsFileGenerator indexer = null;
        try {
            indexer = new PostingsFileGenerator(indexDir);
        } catch (Exception e) {
            log.error("Cannot create index...", e);
            System.exit(-1);
        }

        String path = null;
        try {
            path = args[1];
            // try to add file into the index
            indexer.indexFileOrDirectory(path);
        } catch (Exception e) {
            log.error("Error indexing " + path + " : ", e);
        }
        indexer.closeIndex();
        
        Directory d = FSDirectory.open(new File(indexDir));
        IndexReader r = IndexReader.open(d);

        TermEnum terms = r.terms();
        
        PrintWriter pw = new PrintWriter(new File("postings-list.txt"));
        
        while(terms.next()) {
            Term t = terms.term();
            TermDocs termDocs = r.termDocs(t);
            List<Integer> docIds = new ArrayList<Integer>();
            while(termDocs.next()) {
                docIds.add(termDocs.doc());
            }
            pw.write(t.text() + docIds.toString() + "\n");
        }
        pw.close();
        System.out.println("Number of documents: " + r.numDocs());
    }

    /**
     * Constructor
     * 
     * @param indexDir
     *            the name of the folder in which the index should be created
     * @throws java.io.IOException
     */
    PostingsFileGenerator(String indexDir) throws IOException {
        // the boolean true parameter means to create a new index every time,
        // potentially overwriting any existing files there.
        FSDirectory dir = FSDirectory.open(new File(indexDir));

        StandardAnalyzer analyzer = new StandardAnalyzer(Version.LUCENE_35);

        IndexWriterConfig config = new IndexWriterConfig(Version.LUCENE_35,
                analyzer);
        config.setOpenMode(OpenMode.CREATE);

        writer = new IndexWriter(dir, config);
    }

    /**
     * Indexes a file or directory
     * 
     * @param fileName
     *            the name of a text file or a folder we wish to add to the
     *            index
     * @throws java.io.IOException
     */
    public void indexFileOrDirectory(String fileName) throws IOException {
        addFiles(new File(fileName));

        int originalNumDocs = writer.numDocs();
        for (File f : queue) {
            FileReader fr = null;
            try {
                Document doc = new Document();
                fr = new FileReader(f);
                doc.add(new Field("contents", fr));
                doc.add(new Field("path", fileName, Field.Store.YES,
                        Field.Index.NOT_ANALYZED));
                writer.addDocument(doc);
            } catch (Exception e) {
                log.error("Could not add: " + f, e);
            } finally {
                fr.close();
            }
        }

        int newNumDocs = writer.numDocs();
        System.out.println("");
        System.out.println("************************");
        System.out.println((newNumDocs - originalNumDocs)
                + " documents added.");
        System.out.println("************************");

        queue.clear();
    }

    private void addFiles(File file) {

        if (!file.exists()) {
            log.warn(file + " does not exist.");
        }
        if (file.isDirectory()) {
            for (File f : file.listFiles()) {
                addFiles(f);
            }
        } else {
            queue.add(file);
        }
    }

    /**
     * Close the index.
     * 
     * @throws java.io.IOException
     */
    public void closeIndex() throws IOException {
        writer.close();
    }

}
