"""
Script for calculate word-level diarization error rate (word-level DER)

Input files:
1. reference .txt file in format "speaker №: text"
2. recognized .txt file in format "speaker №: text"

Output file (-r optional for analise) .csv file in format:
Reference speaker | Text | Words count | Result speaker | Text | Error words

In console output result in format:
Word in ref text: number of words
Word with error speaker: number of words
DER: word-level diarization error rate
"""

import difflib
import csv
import argparse
import re


def bring_to_normal(text: str) -> list[str]:
    """ Bringing text into view: 'Speaker <spk_num>: text' """

    text_list = text.split(sep='\n')
    for string in text_list:
        if string.startswith(('0:', '1:', '2:', '3:', '4:', '5:', '6:', '7:', '8:', '9:')):
            text_list.remove(string)

    text_str = ' '.join(text_list)
    text_list = re.split('Спикер|Speaker', text_str)
    if '' in text_list:
        text_list.remove('')
    for ind, string in enumerate(text_list):
        string_split = string.split(':')
        text_list[ind] = 'Speaker ' + ': '.join(string_split)
        for symbol in ('[', '.', ',', '?', '!', '-', ']', '   ', '  '):
            text_list[ind] = text_list[ind].replace(symbol, ' ')
    return text_list


def remove_spk(text: list[str]) -> list[str]:
    """
    remove speakers
    :param text: list of strings in format 'Speaker <spk_num>: text'
    :return: list of strings from text without 'Speaker <spk_num>'
    """
    res = []
    for string in text:
        res += string.split(':')[1].strip().split()
    return res


def matching_spk_word(text: list[str]) -> list[list[str]]:
    """
    matching of speaker-word pairs
    :param text: list of text strings in format 'Speaker <spk_num>: text'
    :return: list with pair [<spk_num>, word]
    """
    res = []
    for string in text:
        if ':' in string:
            split_string = string.split(':')
            for word in split_string[1].split():
                res.append([split_string[0].split()[1], word])
    return res


def diff_word_ind(text_1: list, text_2: list) -> list:
    """
    definition of word indexes (equal and replace)
    :param: pair of lists with words from compared texts
    :return: list of pair word indexes
    """
    indexes_diff = []
    string = difflib.SequenceMatcher(None, text_1, text_2)
    for tag, i_1, i_2, j_1, j_2 in string.get_opcodes():
        if tag in ('equal', 'replace'):
            tmp = [[i_1, i_2], [j_1, j_2]]
            indexes_diff.append(tmp)

    indexes_res = []
    for element in indexes_diff:
        tmp = list(range(*element[0]))
        tmp_1 = list(range(*element[1]))

        if len(tmp) < len(tmp_1):
            for idx, elem in enumerate(tmp):
                indexes_res.append([elem, tmp_1[idx]])
        else:
            for idx, elem in enumerate(tmp_1):
                indexes_res.append([tmp[idx], elem])
    return indexes_res


def match(reference: list[str], recognize: list[str]) -> tuple[str, str]:
    """
    Compare of source files
    :param reference: list of strings from reference text
    :param recognize: list of strings from recognize text
    :return res_reference: reference text in format 'Speaker <spk_num>, text, number of words of this speaker'
    :return res_recognize: recognize text in format ' Speaker <spk_num>, text, number of words if the
    speaker differs from the reference'
    """

    reference_spk_word = matching_spk_word(reference)
    recognize_spk_word = matching_spk_word(recognize)
    indexes_res = diff_word_ind(remove_spk(reference), remove_spk(recognize))

    # matching speaker-word pairs in the original file and the recognized one
    res_reference = 'ref speaker:text:words count'
    res_recognize = 'result speaker:text:error words'
    speaker_old_reference = 0
    speaker_old_recognize = 0
    for element in indexes_res:
        speaker_new_reference = reference_spk_word[element[0]][0]
        speaker_new_recognize = recognize_spk_word[element[1]][0]
        if speaker_old_reference != speaker_new_reference:
            res_reference += f'\nSpeaker {reference_spk_word[element[0]][0]}:'
            res_recognize += f'\nSpeaker {recognize_spk_word[element[1]][0]}:'
            speaker_old_reference = speaker_new_reference
        if speaker_old_recognize != speaker_new_recognize:
            res_recognize += f'\nSpeaker {recognize_spk_word[element[1]][0]}:'
            res_reference += f'\nSpeaker {reference_spk_word[element[0]][0]}:'
            speaker_old_recognize = speaker_new_recognize
        res_reference += f'{reference_spk_word[element[0]][1]} '
        res_recognize += f'{recognize_spk_word[element[1]][1]} '
    return res_reference, res_recognize


def write_result_in_file(res_file: list, res_name: str) -> None:
    """
    Write output file
    :param res_file: list with result table strings
    :param res_name: path to output file
    """
    with open(res_name, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL, delimiter=',')
        for elem in res_file:
            writer.writerow(elem)


def result_count(reference: str, recognize: str) -> list:
    """
    Create output result
    :param reference: reference text in format 'Speaker <spk_num>, text, number of words of this speaker'
    :param recognize: recognize text in format ' Speaker <spk_num>, text, number of words if the speaker differs
    from the reference'
    :return: list with result table strings
    """
    reference = reference.split('\n')
    recognize = recognize.split('\n')
    result = []
    total_word = 0
    spk_error_word = 0

    for ind, elem in enumerate(reference):
        col_3 = ''
        col_6 = ''
        col_1, *col_2 = elem.split(':')
        col_4, *col_5 = recognize[ind].split(':')
        if col_1 != col_4 and ind != 0:
            col_6 = f'{len(col_5[0].split())}'
            spk_error_word += int(col_6)
        elif col_1 == col_4 and ind != 0:
            col_6 = '0'
        if col_2 and ind != 0:
            col_3 = len(col_2[0].split())
            total_word += int(col_3)
        if ind == 0:
            result.append([col_1, *col_2, col_4, *col_5, col_6])
        if col_2 != [''] and col_5 != [''] and ind != 0:
            result.append([col_1, *col_2, col_3, col_4, *col_5, col_6])
    print(f'Word in ref text: {total_word}\n'
          f'Word with error speaker: {spk_error_word}\n'
          f'der: {spk_error_word / total_word}')
    return result


def main():

    parser = argparse.ArgumentParser(
        description='match reference and recognise files for analise speaker error rate'
    )
    parser.add_argument('reference', type=str, help='Input reference file')
    parser.add_argument('recognized', type=str, help='Input recognized file')
    parser.add_argument('-o', '--output',
                        type=str,
                        default=None,
                        help='Output result file, default: None')
    args = parser.parse_args()

    with open(args.reference, 'r', encoding='utf-8') as orig:
        reference_text = bring_to_normal(orig.read())
    with open(args.recognized, 'r', encoding='utf-8') as recognized:
        recognized_text = bring_to_normal(recognized.read())

    res_orig, res_error = match(reference_text, recognized_text)
    result_table = result_count(res_orig, res_error)
    if args.result:
        write_result_in_file(result_table, args.output)


if __name__ == '__main__':
    main()
