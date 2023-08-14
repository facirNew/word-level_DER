# word-level_DER
Script for calculate word-level diarization error rate (word-level DER)

input files:
1. reference .txt file in format "speaker №: text"
2. recognized .txt file in format "speaker №: text"

output file (-r optional for analise)
1 .csv file in format:
reference speaker | text | words count | result speaker | text | error words

In console output result in format:
Word in ref text: number of words
Word with error speaker: number of words
DER: word-level diarization error rate
