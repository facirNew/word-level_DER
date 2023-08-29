# word-level_DER
Script for calculate word-level diarization error rate (word-level DER)

Input files:
1. Reference .txt file in format "speaker <spk_number>: text"
2. Recognized .txt file in format "speaker <spk_number>: text"

Output file (-r optional for analise)
.csv file in format:
Reference speaker | Text | Words count | Result speaker | Text | Error words

In console output result in format:
Word in ref text: number of words
Word with error speaker: number of words
DER: word-level diarization error rate
