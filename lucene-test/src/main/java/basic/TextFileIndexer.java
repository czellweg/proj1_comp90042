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
 * THIS CLASS HAS BEEN COPIED FROM:
 * http://www.lucenetutorial.com/sample-apps/textfileindexer-java.html Several
 * changes have been made to fit my use case.
 */

public class TextFileIndexer {

    private static final Logger log = Logger.getLogger(TextFileIndexer.class);

    private IndexWriter writer;
    private List<File> queue = new ArrayList<File>();

    public static void main(String[] args) throws IOException {

        String indexDir = "/Users/zaeggi/UniMelbourne/semester3/comp90042_websearch/project1/index-dir";
        TextFileIndexer indexer = null;
        try {
            indexer = new TextFileIndexer(indexDir);
        } catch (Exception e) {
            log.error("Cannot create index...", e);
            System.exit(-1);
        }

        // ===================================================
        // read input from user until he enters q for quit
        // ===================================================
        String path = null;
        try {
            path = "/Users/zaeggi/UniMelbourne/semester3/comp90042_websearch/project1/reuters/test";
            // try to add file into the index
            indexer.indexFileOrDirectory(path);
        } catch (Exception e) {
            log.error("Error indexing " + path + " : ", e);
        }

        // ===================================================
        // after adding, we always have to call the
        // closeIndex, otherwise the index is not created
        // ===================================================
        indexer.closeIndex();

        Directory d = FSDirectory.open(new File(indexDir));
        IndexReader r = IndexReader.open(d);

        TermEnum terms = r.terms();
        
        PrintWriter pw = new PrintWriter(new File("output.txt"));
        
        Map<String, List<Integer>> postings = new HashMap<String, List<Integer>>();
        while(terms.next()) {
            Term t = terms.term();
            TermDocs termDocs = r.termDocs(t);
            List<Integer> docIds = new ArrayList<Integer>();
            while(termDocs.next()) {
                docIds.add(termDocs.doc());
            }
            System.out.println(t.text());
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
    TextFileIndexer(String indexDir) throws IOException {
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
        // ===================================================
        // gets the list of files in a folder (if user has submitted
        // the name of a folder) or gets a single file name (is user
        // has submitted only the file name)
        // ===================================================
        addFiles(new File(fileName));

        int originalNumDocs = writer.numDocs();
        for (File f : queue) {
            FileReader fr = null;
            try {
                Document doc = new Document();

                // ===================================================
                // add contents of file
                // ===================================================
                fr = new FileReader(f);
                doc.add(new Field("contents", fr));

                // ===================================================
                // adding second field which contains the path of the file
                // ===================================================
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
