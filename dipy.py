############################
## dipy.py
##
## written by Kevin Doyle
##
## Reformats a narrative blog story into
## conversational format
##
## editing: Points of interest are
##          labelled with DBUG or NOTE
############################



import nltk
import re
import random
import os
import sys
from random import shuffle

story = ""
sent_count = -1
sentences = []
sent_word_array = [] # These two arrays can be zipped
pos_word_array = []  # and iterated through together
tagged_word_array = [] # [sentence][word] array with TAGS inserted
tagged_pos_array = [] # [sentence][pos] 
tag_record_array = [] # stores record of TAGS. index corresponds with sentence index
word_comma_storage_array = [] # [sentence][word] index corresponds with sentences
storage_array = [] # [sentence][ (word, tag) ]
formatted_output = []
selection_numbers = set([1, 2, 3, 4])

def repopulate_selection_numbers():
   global selection_numbers
   selection_numbers = set([1, 2, 3, 4])

def question_phrase( topic ):
   global selection_numbers
   question = ""
   
   try:
      selection = selection_numbers.pop()
   except KeyError:
      repopulate_selection_numbers()
      selection = selection_numbers.pop()
      
   if selection == 1:
      question = "Wasn't there something more about the {0}?".format( topic )
   elif selection == 2:
      question = "The {0}... I'm not remembering the next part, keep going.".format( topic )
   elif selection == 3:
      question = "What else was there about the {0}?".format( topic )
   elif selection == 4:
      question = "The {0}... I'm not remembering the next part, keep going.".format( topic )

   return nltk.word_tokenize( question )

def conj_split( sent ):
   first = []
   second = []
   split = False

   for word in sent:
      if word == "but":
         split = True
      if split:
         second.append( word )
      else:
         first.append( word )
   
   return ( first, second )
   
# Checks for specific POS patterns
# NOTE: 2014-11-10 If a sentence matches the given pattern twice or 
#       more, currently only the last match is stored and returned.
# NOTE: 2014-11-10 Please change the name of this function, it is not
#       simulating entrainment
def entrain( word_list, pos_list ):
   global storage_array
   have_dt = have_nn = have_vb = have_in = have_prp = have_nn2 = False
   dt = nn = vb = ni = prp = nn2 = ""
   phrase = []
   reset = False
   
   # Collapses the POS list into a single string
   pos_mash = ''.join( pos_list )
   
   # A regex pattern is used to check for the existence of the desired
   # pattern within the POS string 
   match = re.search( r'DTNN.?VBDIN', pos_mash )
   
   # If the regex pattern matches, then the following is used to 
   # extract the words with correspond with the POS pattern
   if match is not None:
      for ( idx, word ), pos in zip( enumerate( word_list ), pos_list ):

         # If a POS matches, a boolean is changed to allow for the
         # next match to be assessed. 
         if pos == "DT":
            dt = word
            have_dt = True
         elif have_dt and pos.startswith( 'N' ):
            nn = word
            have_nn = True
            have_dt = False
         elif have_nn and pos.startswith( 'VBD' ):
            vb = word
            have_vb = True
            #have_nn = False DBUG: 2014-11-10 I think these should be added, cant test right now so leaving commented out
            #have_dt = False
         elif have_vb and pos == "IN":
            ni = word
            have_in = True
            #have_dt = False DBUG: see above
            #have_nn = False
            have_vb = False
            phrase = [ dt, nn, vb, ni ]
            
         # At this point, the original pattern has been matched and
         # saved into 'phrase'. The following is a check for an 
         # extension of the original pattern, adding PRP$ N.? 
         # to account for the indefinite IN leading to a speaker's
         # possession. 
         elif have_in and pos == "PRP$":
            prp = word
            have_prp = True
         elif have_prp and pos.startswith( 'N' ):
            if nn2 == "":
               nn2 = word 
            else:
               nn2 = nn2 + ' ' + word
            have_nn2 = True
         elif have_nn2:
            phrase = [ "a", nn, vb, ni, prp, nn2 ]
            reset = True
         else:
            reset = True
            
         # Resets all boolean values, to prep for next iteration
         if reset:
            have_dt = False
            have_nn = False
            have_vb = False
            have_in = False
            have_prp = False
            have_nn2 = False
            dt = nn = vb = ni = prp = nn2 = ""
            reset = False
   
   return phrase
   
def process_text( stry ):
   global story
   global sentences
   global sent_count 
   global sent_word_array
   global pos_word_array
   global tagged_word_array
   global tagged_pos_array
   global word_comma_storage_array
   global tag_record_array
   global storage_array
   
   # Stores the raw story
   story = stry
   
   # Stores the raw sentences in an array
   sentences = nltk.sent_tokenize( story )
   
   # A count of the sentences
   sent_count = len( sentences )
   
   # Creates an array of sentences, stored as word tokens
   # Stores complementary array with part of speech tags
   temp_wa = []
   temp_pos = []
   for sent in sentences:
      temp_wa = nltk.word_tokenize( sent )
      temp_pos = [ pos for word, pos in nltk.pos_tag( temp_wa ) ]
      # Remove the capital from the first word in the sentence
      # If the word is not tagged as a proper noun
      if temp_pos[0] is not 'NNP':
         temp_wa[0] = temp_wa[0].lower()
      assert len( temp_wa ) == len( temp_pos ), "Word/POS indexing mismatch"  
      sent_word_array.append( temp_wa )
      pos_word_array.append( temp_pos )
      
   # Creates copies
   tagged_word_array = list( sent_word_array )
   tagged_pos_array = list( pos_word_array )
   
   # Initialize empty arrays
   word_comma_storage_array = [ [] for sent in sentences ]
   tag_record_array = [ [] for sent in sentences ]
   storage_array = [ [] for sent in sentences ]
   
def pronoun_replacer( ):
   global tagged_word_array
   global tagged_pos_array
   
   for word_list, pos_list in zip( tagged_word_array, tagged_pos_array ):
      for ( idx, word ), pos in zip( enumerate( word_list ), pos_list ):
         if word == 'I':
            word_list.pop( idx )
            word_list.insert( idx, "we" )
         if word == 'i':
            word_list.pop( idx )
            word_list.insert( idx, "we" )
         if word == 'my':
            word_list.pop( idx )
            word_list.insert( idx, "our" )
         if word == 'My':
            word_list.pop( idx )
            word_list.insert( idx, "our" )
         if word == 'you':
            word_list.pop( idx )
            word_list.insert( idx, "people" )
            
      
def initial_tagging( ):
   global tagged_word_array
   global tagged_pos_array
   global tag_record_array
   global word_comma_storage_array 
   
   # Check for "Word, " at the beginning of each sentence
   # If the pattern is found, the word and comma are removed from the sentence
   # the place is held by WC_TAG, the word is placed into word_comma_storage_array,
   # and a note is added to tag_record_array
   for (idx, sentence), pos in zip( enumerate( tagged_word_array ), tagged_pos_array ):
      if sentence[1] == ',':
         word_comma_storage_array[idx].append( sentence.pop(0) )
         assert sentence.pop(0) == ',', "The WC pop removed a word"
         pos.pop(0)
         pos.pop(0)
         tag_record_array[idx].append( "WC_TAG" )

# Fills an array with tags for edits applicable to each corresponding
# sentence
def edit_tagging( ):
   global tagged_word_array
   global tagged_pos_array
   global tag_record_array
   global word_comma_storage_array 
   global storage_array
   prev_nouns = set()
   conj_words = set( ['but'] )
   
   #Types of edits:
   # First Sentence
   # Patterned "Yeah"'s
   # Running Topic
   # Entrainment grammar match
   # Conjugation
   
   for (idx, sent), pos_sent in zip( enumerate( tagged_word_array ), tagged_pos_array ):
   
      # First sentence is tagged
      if idx == 0:
      
         # First Sentence
         tag_record_array[idx].append( "FIRST_TAG" )
         
      # Every fifth sentence, starting at the second, is tagged 
      if (idx + 1) % 5 is 2:
      
         # Yeah,
         tag_record_array[idx].append( "YEAH_TAG" )
         
      # Create a set of nouns from the current sentence
      current_nouns = set( [ word for word, pos in zip( tagged_word_array[idx], tagged_pos_array[idx] ) if pos.startswith('N') ] )
      
      # Union with set from previous sentence, check for common terms
      if len( prev_nouns & current_nouns ) > 0:
      
         # Running Topic
         # Overlapping nouns are saved
         topic_nouns = prev_nouns & current_nouns
         storage_array[idx].append( ( topic_nouns.pop(), "TOPIC_TAG" ) )
         tag_record_array[idx].append( "TOPIC_TAG" )
         
      # Current is assigned to prev, for use in next iteration
      prev_nouns = current_nouns 
         
      # Checks for a rule-determined POS pattern, returns words
      repeat_phrase = entrain( sent, pos_sent )
      
      # Verifies that a match was made
      if len( repeat_phrase ) > 1:
      
         # Repeat Phrase
         # Tags the next sentence with "ENTRAIN_TAG" and stores the
         # phrase, because the phrase will be inserted into the following
         # sentence at a later point
         storage_array[idx+1].append( ( repeat_phrase, "ENTRAIN_TAG" ) )
         tag_record_array[idx+1].append( "ENTRAIN_TAG" )
         
      # Checks the sentence for words associated with conjugation
      # NOTE: 2014-11-10 Currently 'but' is the only conjugation case 
      #       dealt with by this function
      if len( set( sent ) & conj_words ) > 0:
         # Conjugation
         tag_record_array[idx].append( "CONJ_TAG" )
          
def edit_mixer( ):
   global tag_record_array
   global sent_count
   tag_record_revision = [ [] for tags in tag_record_array ]
   r = random.random()
   tag_chooser = [ "TOPIC_TAG", "ENTRAIN_TAG" ]
   shuffle( tag_chooser, lambda: r )
   waiting = True
   skip_1 = skip_2 = False
   skip = 0
   
   for idx, tags in enumerate( tag_record_array ):
      if not skip_1 and skip <= 0 and tags.count( tag_chooser[0] ) > 0:
         tag_record_revision[idx].append( tag_chooser[0] )
         skip_2 = True
         skip = 2
         waiting = False
      elif not skip_2 and skip <= 0 and not waiting and tags.count( tag_chooser[1] ) > 0:
         tag_record_revision[idx].append( tag_chooser[1] )
         skip_1 = True
         skip = 2
      elif skip <= 0:
         tag_record_revision[idx] = list( tags )
      else:
         skip -= 1
         skip_1 = False
         skip_2 = False
      
   #for tags in tag_record_revision:
   #   print tags
   assert len( tag_record_array ) == len( tag_record_revision ), "Tag Records Length Mismatch"
   tag_record_array = tag_record_revision
         
# Applies rules for edit distribution
def edit_planner( ):
   global tag_record_array
   global sent_count
   wc = False
   
   # NOTE: 2014-11-10 This only deals with two tags,
   #       and doesn't allow for any interesting combinations
   #       to occur. This should be re-examined
   
   # Iterates through each list of tags for each sentence
   for idx, tags in enumerate( tag_record_array ):
   
      # TOPIC_TAG check
      if tags.count( "TOPIC_TAG" ) > 0:
         # Priority is given to the running topic tags,
         # they are distributed first.
         
         # Removes all tags from this sentence
         # DBUG: 2014-11-10 is this needed? Why? Run some tests without
         while len( tag_record_array[idx] ) > 0:
            temp = tag_record_array[idx].pop()
            if temp == "WC_TAG":
               wc = True
         if wc:
            tag_record_array[idx].append( "WC_TAG" )
            wc = False
         tag_record_array[idx].append( "TOPIC_TAG" )
         
         # Removes all tags from the following sentence,
         # appends ACK_TAG, an acknowledgement for the running topic
         try:
            while len( tag_record_array[idx+1] ) > 0:
               temp = tag_record_array[idx+1].pop()
               if temp == "WC_TAG":
                  wc = True
            if wc:
               tag_record_array[idx+1].append( "WC_TAG" )
               wc = False
         except IndexError:
            pass
         tag_record_array[idx+1].append( "ACK_TAG" )
         
      # ENTRAIN_TAG check
      if tags.count( "ENTRAIN_TAG" ) > 0:
      
         # Removes all tags from sentence
         # DBUG: 2014-11-10 Is this needed? Try without.
         while len( tag_record_array[idx] ) > 0:
            temp = tag_record_array[idx].pop()
            if temp == "WC_TAG":
               wc = True
         if wc:
            tag_record_array[idx].append( "WC_TAG" )
            wc = False
            
         # Removes tags from following sentence
         try:
            while len( tag_record_array[idx+1] ) > 0:
               temp = tag_record_array[idx+1].pop()
               if temp == "WC_TAG":
                  wc = True
            if wc:
               tag_record_array[idx+1].append( "WC_TAG" )
               wc = False
         except IndexError:
            pass
         
         # Reapplies the ENTRAIN_TAG once other tags have been cleared
         tag_record_array[idx].append( "ENTRAIN_TAG" )
   
def edit_applicator( ):
   global tagged_word_array
   global tagged_pos_array
   global tag_record_array
   global word_comma_storage_array 
   global storage_array
   offset = 0
   ref = -1
   
   array_len =  len(tagged_word_array)
   
   #FIRST_TAG YEAH_TAG TOPIC_TAG ENTRAIN_TAG CONJ_TAG WC_TAG ACK_TAG
   # TODO: create a new array of sents for final output. output_sent_array 
   for (idx, sent) in enumerate( tagged_word_array ):
     if idx < (array_len / 3): # NOTE: 2014-11-10 What does this do? Is this for blocking out a chunk of text for edits? 
      for tag in tag_record_array[idx-offset]:
         ref = idx-offset
         
         if tag == "WC_TAG":
            sent.insert( 0, "{0},".format( word_comma_storage_array[idx-offset][0] ) )
            
         if tag == "FIRST_TAG":
            sent.insert( 0, "So, here's the thing." )
            
         if tag == "TOPIC_TAG":
            tagged_word_array.insert( idx, question_phrase( storage_array[idx-offset][0][0] ) )
            offset += 1
            
         if tag == "ACK_TAG":
            sent.insert( 0, "Right!" ) # TODO: Random selector for acknowledgement
            
         if tag == "ENTRAIN_TAG":
            sent.insert( 0, "Uh huh, {0}.".format( ' '.join( storage_array[idx-offset][0][0] ) ) )
            
         if tag == "CONJ_TAG":
            temp = tagged_word_array.pop(idx)
            ( first, second ) = conj_split( temp )
            if idx-1 >= 0:
               tagged_word_array.insert( idx, second )
               tagged_word_array.insert( idx, first )
               offset += 1
            else:
               tagged_word_array.insert( idx, temp )
               
         if tag == "YEAH_TAG":
            sent.insert( 0, "Yeah," )
            
      while len( tag_record_array[ref] ) > 0:
         tag_record_array[ref].pop()
   
   
def formatting_fixer( ):
   global tagged_word_array
   global formatted_output
   prev_word = ""
   
   for word_list in tagged_word_array:
      temp = []
      for idx, word in enumerate( word_list ):
         if idx == 0:
            word = "{0}{1}".format( word[0].upper(), word[1:] )
            
         if prev_word.endswith( '.' ) or prev_word.endswith( '!' ):
            word = "{0}{1}".format( word[0].upper(), word[1:] )

         if word.startswith( "'" ) or word.startswith( '.' ) or word.startswith( ',' ) or word.startswith( '!' ) or word.startswith( "n'" ) or word.startswith( '?' ):
            temp.pop()
            temp.append( "{0}{1}".format( prev_word, word ) )
            prev_word = "{0}{1}".format( prev_word, word )
         else:
            prev_word = word
            temp.append( word )
   
      formatted_output.append( temp )
      
def chunk_text( chunk_size ):
   global formatted_output
   
   word_count = 0
   noun_set = set()
   
   if chunk_size > 0:
      for idx, sent in enumerate(formatted_output):
         word_count = word_count + len(sent)
         if word_count >= chunk_size :
            formatted_output.insert(idx, ['MARKER'])
            word_count = 0
   else:
      for (idx,sent),pos in zip(enumerate(tagged_word_array),tagged_pos_array):
         print pos
         print sent
         print "\n"
      
         # Sentence beings with pronoun, no marker
         if pos[0] == 'PRP':
            continue
         # Sentence begins with adverb, insert marker
         if pos[0].endswith('RB'):
            formatted_output.insert(idx-1, ['MARKER'])
         # Beings with DT, check for overlapping nouns
         # IDEA: Maybe just change topic when pos[0] in sent before DT was PRP
         if pos[0] == 'DT':
            temp_noun_set = set()
            for idx1, part in enumerate(pos):
               if part.startswith('N'):
                  temp_noun_set.add(sent[idx1])
            noun_set = temp_noun_set & noun_set
            if len(noun_set) == 0:
               formatted_output.insert(idx-1, ['MARKER'])
            #if tagged_pos_array[idx-1] == 'PRP':  
            #   formatted_output.insert(idx-1, ['MARKER'])
               
               
def generate_output( file ):
   global formatted_output
   num = 0
   file_name = "./output/{0}.txt".format( file )
   dir = os.path.dirname( file_name )
   if not os.path.exists( dir ):
      os.makedirs( dir )
   f = open( file_name, "w" )
   
   idx_offset = 0
   for idx, sent in enumerate( formatted_output ):
      idx = idx - idx_offset
      if sent == ['MARKER']:
         f.write( "{0}\n".format( ' '.join( sent ) ) )
         idx_offset = idx_offset + 1
      elif (idx % 2) is 0:
         num += 1
         f.write( "A{0}: {1}\n".format( num, ' '.join( sent ) ) )
      else:
         f.write( "B{0}: {1}\n".format( num, ' '.join( sent ) ) )
         
   f.close()
   
def reset( ):
   global story
   global sent_count
   global sentences
   global sent_word_array
   global pos_word_array
   global tagged_word_array
   global tagged_pos_array
   global tag_record_array
   global word_comma_storage_array
   global storage_array
   global formatted_output
   global selection_numbers
   
   story = ""
   sent_count = -1
   sentences = []
   sent_word_array = [] # These two arrays can be zipped
   pos_word_array = []  # and iterated through together
   tagged_word_array = [] # [sentence][word] array with TAGS inserted
   tagged_pos_array = [] # [sentence][pos] 
   tag_record_array = [] # stores record of TAGS. index corresponds with sentence index
   word_comma_storage_array = [] # [sentence][word] index corresponds with sentences
   storage_array = [] # [sentence][ (word, tag) ]
   formatted_output = []
   selection_numbers = set([1, 2, 3, 4])
         
if __name__ == '__main__':

   # Reads in command line argument for story file, or prompts user
   if len(sys.argv) > 1:
      story_name = sys.argv[1]
   else:
      story_name = raw_input("Please enter name of story file --> ")
   
   # Sets up all of the arrays
   process_text( open( story_name ).read() )
   
   pronoun_replacer( )
   
   # Tags for conversational language which may already exist in the text
   #initial_tagging( )
   
   # Sets tags for lines where edits are possible
   #edit_tagging( )
   
   # Analyses the distribution of possible edits
   # TODO: This does not exist yet
   #edit_analysis( )
   
   # Mixes up the edit tags in order to vary the output
   #edit_mixer( )
   
   #edit_planner( )
   
   #edit_applicator( )

   formatting_fixer( )
   
   chunk_size = 0
   chunk_text( chunk_size )
   
   print formatted_output
   
   generate_output( "{0}_standard".format( story_name[:-4] ) )
   
   print "Standard output complete"
   """
   for num in xrange(0, 5):
      reset( )
      process_text( open( story_name ).read() )
      pronoun_replacer( )
      #initial_tagging( )
      #edit_tagging( )
      #edit_mixer( )
      #edit_planner( )
      #edit_applicator( )
      formatting_fixer( )
      generate_output( "{0}_{1}".format( story_name[:-4], num ) )
   """
   print "...done!"
    
   
   #for word_list in formatted_output:
   #  print "{0}\n".format( ' '.join( word_list ) )
 
   #for word_list in tagged_word_array:
   #  print "{0}".format( ' '.join( word_list ) ) 
         
   #for word, tag, word_list in zip( storage_array, tag_record_array, tagged_word_array ):
   #   print "{0}".format( ' '.join( word_list ) )
   #   print "{0}  {1} \n\n".format( word, tag )
   
         