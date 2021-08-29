import java.util.*;

public class alphabetAnimals{

    public static void main(String args[]){
        Scanner keyboard = new Scanner(System.in);
        Scanner sc = new Scanner(System.in);

        // find length for array
        int lines = 0;
        while(sc.hasNextLine()){
            lines++;
            sc.nextLine();
        }
        // create array to hold names
        String [] names = [lines];
        // alphabet array
        //String [] letters = "a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z";

        int letters[] = new int[26];
        for (int i=0; i < letters.length; i++){
            letters[i] = 0;
        }

        
        // load in animal names from user input
        for(int i = 0; i < lines; i++){
            names[i] = keyboard.nextLine();
        }

        String firstName = names[0];
        for (int j = 2; j < names.length-1; j++){
            // name follows first letter /last letter rule (output name)
            if(firstName.charAt(firstName.length-1).equals(names[j].charAt(0))){
                
                if(names[j].charAt(names[j].length-1).equals(names[j+1])){
                    System.out.print(names[j]);
                }
                
            }
            // name eliminates next player, (output name!)

        }
    }
}