import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Scanner;

public class Repeats {
    public static double start;

    public static Path file;
    /**
     * checks whether the alphabet symbols are valid
     * 
     * @param seq String value of argument given
     * @return true if seq is in alphabet, false otherwise
     */
    public static boolean checkSymbol(String seq) {
        boolean symbol = true;
        for (int i = 0; i < seq.length(); i++) {
            if (!(seq.charAt(i) == 'A' || seq.charAt(i) == 'C' || seq.charAt(i) == 'G' || seq.charAt(i) == 'T')) {
                symbol = false;
                return symbol;

            }
        }
        return symbol;
    }

    /**
     * main logic for comparing repetitions for input String, output of repeated
     * Strings written to txt file
     * 
     * @param mode
     * @param seq      String sequence being tested for repetitions
     * @param filePath file which contains string sequence
     * @throws IOException
     */
    public static void mode1(int mode, String seq, Path filePath) throws IOException {

        // creating and finding filepath for filewriter
        String fileName = filePath.toString();

        String ext = "";
        if (mode == 1) {
            ext = "_chk";
        }
        if (mode == 2) {
            ext = "_bf";
        }
        if (mode == 3) {
            ext = "_opt";
        }

        Scanner scan = new Scanner(fileName).useDelimiter("/mode1/");
        String t = scan.next();
        String next = scan.next();

        Scanner sc = new Scanner(next).useDelimiter("/");
        String t1 = sc.next();
        String t2 = sc.next();
        Scanner scr = new Scanner(t2).useDelimiter(".");
        String t3 = scr.next();

        String file = "../out/" + t1 + t3 + ext + ".txt";
        FileWriter myWriter = new FileWriter(new File(file));

        boolean rep = false;
        for (int i = 0; i < seq.length(); i++) {
            String temp = seq.charAt(i) + "";
            for (int j = i + 1; j < seq.length(); j++) {

                if (temp.compareTo(seq.charAt(j) + "") == 0) {
                    if (seq.substring(i, j + 1).length() != seq.length()) {
                        String word = seq.substring(i, j + 1);

                        for (int z = i + 1; z < seq.length(); z++) {

                            if ((z + word.length() <= seq.length())
                                    && (word.compareTo(seq.substring(z, z + word.length())) == 0)) {
                                myWriter.append(word + " " + i + " " + z + "\n");
                                rep = true;
                            }
                        }

                    }

                }

            }
        }

        if (rep == false) {
            myWriter.append("None");
        }
        myWriter.close();

    }

    /**
     * gets the alphabet symbols needed, also tests if arg size is greater than 4
     * 
     * @param alphabetSize int value from args
     * @return String alphabet symbols
     */
    public static String getAlphabet(int alphabetSize) {
        String alp = "ACGT";
        if (alp.length() < alphabetSize) {
            alphabetSize = 4;
        }
        return alp.substring(0, alphabetSize);
    }

    /**
     * mode1 method copy, tests if argument String has repetitions
     * 
     * @param seq String input being tested
     * @return true if there are repetitions, false otherwise
     */
    public static boolean checkRepeats(String seq) {
        boolean rep = false;
        for (int i = 0; i < seq.length(); i++) {
            String temp = seq.charAt(i) + "";
            for (int j = i + 1; j < seq.length(); j++) {

                if (temp.compareTo(seq.charAt(j) + "") == 0) {
                    if (seq.substring(i, j + 1).length() != seq.length()) {
                        String word = seq.substring(i, j + 1);

                        for (int z = i + 1; z < seq.length(); z++) {

                            if ((z + word.length() <= seq.length())
                                    && (word.compareTo(seq.substring(z, z + word.length())) == 0)) {
                                rep = true;
                                return rep;
                            }
                        }

                    }

                }

            }
        }

        return rep;

    }

    /**
     * main logic for creating strings that dont repeat
     * 
     * @param alphabetSize int size of alphabet symbols
     * @param startSymbol  String symbol of each starting character
     * @param maxSize      int maximum length for repeated strings
     * @throws IOException
     */
    public static void mode2(int alphabetSize, String startSymbol, int maxSize) throws IOException {
        // finding and creating filepath for output to be stored in txt file
        int fileNum = 1;
        boolean stop = false;
        try {
            while (stop == false) {
                FileReader e;
                if (new FileReader("../out/gen" + fileNum + "_bf.txt").read() == -1) {
                    stop = true;
                } else {
                    fileNum++;
                }
            }
        } catch (Exception e) {
        }
        FileWriter fw = new FileWriter(
                ("../out/gen" + (fileNum) + "_bf.txt"));

        String ss = startSymbol;
        String alphabet = getAlphabet(alphabetSize);
        ArrayList<String> nonRepeats = new ArrayList<String>();
        int count = 1;

        nonRepeats.add(ss);
        boolean endC = false;
        int maxS = maxSize;
        boolean acc = true;
        fw.append(ss.length() + " - " + ss + "\n");

        if (maxS == 0) {
            acc = false;
        }

        for (int j = 0; j < nonRepeats.size(); j++) {
            for (int z = 0; z < alphabet.length(); z++) {
                String test = nonRepeats.get(j) + alphabet.charAt(z);
                if (test.length() > maxS && acc == true) {
                    endC = true;
                    fw.close();
                    return;
                }
                if (checkRepeats(test) == false) {
                    count++;
                    int len = test.length();
                    nonRepeats.add(test);
                    fw.append(len + " - " + test + "\n");
                }

            }

        }
        fw.close();
    }


/**
 * Main logic for generating longest possible unrepeating string under given parameters
 * @param alphabetSize size of subset {A,C,G,T}
 * @param startSymbol character that string needs to start with
 * @param runTime time in double for program to run within
 * @throws IOException
 */
    public static void mode3(int alphabetSize, String startSymbol, double runTime) throws IOException {
        
        double now = System.currentTimeMillis();
        // finding and creating filepath for output to be stored in txt file
        int fileNum = 1;
        File f;
        try {
            while (fileNum!=-1) {
                f=new File("../out/out"+(fileNum)+"_opt.txt");
                if(f.exists()){
                    fileNum++;
                }else{
                    break;
                }
            }   
        } catch (Exception e) {
            //TODO: handle exception
        }
        FileWriter fw = new FileWriter(("../out/out" + (fileNum) + "_opt.txt"));

                String alphabet = getAlphabet(alphabetSize);
                ArrayList<String> nonRepeats = new ArrayList<String>();
                int tempLength=0;
                nonRepeats.add(startSymbol);
                String temp="";
        
                for (int j = 0; j < nonRepeats.size(); j++) {
                    for (int z = 0; z < alphabet.length(); z++) {
                        String test = nonRepeats.get(j) + alphabet.charAt(z);

                        if (checkRepeats(test) == false) {
                            tempLength = test.length();
                            nonRepeats.add(test);
                            temp=test;
                            
        
                        }
        
                    }
        
                }
                fw.append(tempLength+" - "+temp);
                fw.close();
                return;
    }





        /**
     * main method, error handling catching, if no errors are caught, specified mode
     * is ran
     * 
     * @param args input variables tested for errors
     * @throws IOException
     */
    public static void main(String args[]) throws IOException {

        if (args.length < 2 || args.length > 4) {
            System.err.println("ERROR: invalid number of arguments");
            return;
        } else {
            switch (args.length) {
                case 2:
                    try {
                        String m = args[0];
                        int mode = Integer.parseInt(m);
                        if (mode != 1) {
                            System.err.println("ERROR: invalid mode");

                            return;
                        } else {
                            try {
                                file = Path.of(args[1]);
                                Scanner sc = new Scanner(new File(file.toString()));
                                String seq = sc.next();
                                if (checkSymbol(seq) == false) {
                                    System.err.println("ERROR: invalid alphabet symbol");
                                    return;
                                } else {

                                    mode1(mode, seq, file);
                                }
                            } catch (Exception e) {
                                // TODO: handle exception
                                System.err.println("ERROR: invalid or missing file");
                                return;
                            }
                        }
                    } catch (Exception e) {
                        // TODO: handle exception
                        System.err.println("ERROR: invalid argument type");
                        return;
                    }

                    break;
                case 3:
                    System.err.println("ERROR: invalid number of arguments");

                    break;
                case 4:

                    try {
                        int mode = Integer.parseInt(args[0]);
                        int alphabetSize = Integer.parseInt(args[1]);
                        //int max = Integer.parseInt(args[3]);

                        if (mode != 2 && mode != 3) {
                            System.err.println("ERROR: invalid mode");
                            return;
                        } else {
                            if (mode == 2) {
                                if (checkSymbol(args[2]) == false || args[2].length() > 1) {
                                    System.err.println("ERROR: invalid alphabet symbol");
                                    return;
                                } else {
                                    mode2(Integer.parseInt(args[1]), args[2], Integer.parseInt(args[3]));
                                }
                            }else{
                                if (checkSymbol(args[2]) == false || args[2].length() > 1) {
                                    System.err.println("ERROR: invalid alphabet symbol");
                                    return;
                                } else {
                                    start=System.currentTimeMillis();
                                    mode3(Integer.parseInt(args[1]), args[2], Double.parseDouble(args[3]));
                                }
                            }
                        }
                    } catch (Exception e) {
                        // TODO: handle exception
                        System.err.println("ERROR: invalid argument type");
                        return;
                    }

                    break;

            }
        }

    }
}