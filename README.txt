Documentation of dipy.py
written by Kevin Doyle

------------------------
-------2014 11 10-------
------------------------

Order of function calls in main:
   process_text( open( story_name ).read() )
   pronoun_replacer( )
   initial_tagging( )
   edit_tagging( )
   #edit_analysis( )
   #edit_mixer( )
   edit_planner( )
   edit_applicator( )
   formatting_fixer( )
   generate_output( )


initial_tagging():
   - Removes from the beginning of sentences, a word followed by a comma. General: "<word>," Example: "Then," 
   - The word is stored, and the marker "WC_TAG" is given to the sentence.
   
edit_tagging():

   Found in edit_tagging(): 
      #Types of edits:
      # First Sentence
      # Patterned "Yeah"'s
      # Running Topic
      # Entrainment grammar match
      # Conjugation
      
   These appear to be the current types of possible edits. The edits are identified as follows:
   
   First Sentence: 
      The sentence indexed as zero is marked FIRST_TAG
   
   Patterned "Yeah"'s: 
      Every fifth sentence index, starting with the second sentence, is marked "YEAH_TAG"

   Running Topic:
      - A set of nouns from the sentence is assembled 
      - The new set is compared with a set which was constructed with the previous sentence, checking for overlaps.
      - If overlaps exist, the overlapped nouns are saved and the sentence is marked "TOPIC_TAG"
   
   Repeat Phrase:
      - The sentence and it's POS tags are sent to a function 'entrain'
      - See entrain() comments
      - If the desired POS pattern is found, the corresponding words are stored and the NEXT sentence (the one after this which was searched) is marked with "ENTRAIN_TAG" --NOTE: entrain() and ENTRAIN_TAG will be renamed to something reflecting repetition
      
   Conjugation:
      - Checks sentence for words used in conjugation
      - If found, sentence is given marker "CONJ_TAG"
      
edit_planner():
   
   Needs to be re-examined. This function currently clears out all edits occurring around TOPIC_TAG or ENTRAIN_TAG tags, that is all.
      
Other Functions:
   
      entrain( word_list, pos_list )
      