"""
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
"""

import difflib
import csv
import argparse
import re


def cleaning(file: str) -> str:
    """
    bringing files back to normal
    :param file: text for cleaning
    :return: file in format 'Speaker No.: text'
    """
    file_list = file.split(sep='\n')
    for elem in file_list:
        if elem.startswith(('0:', '1:', '2:', '3:', '4:', '5:', '6:', '7:', '8:', '9:')):
            file_list.remove(elem)

    file_str = ' '.join(file_list)
    file_list = re.split('Спикер|Speaker', file_str)
    file_list.remove('')
    for ind, elem in enumerate(file_list):
        tmp = elem.split(':')
        file_list[ind] = 'Speaker ' + ': '.join(tmp)
        file_list[ind] = file_list[ind].replace('[', ' ').\
            replace('.', ' ').replace(',', ' ').replace('?', ' ').\
            replace('!', ' ').replace('-', ' ').replace(']', ' ').\
            replace('   ', ' ').replace('  ', ' ')
    file_str = '\n'.join(file_list)
    return file_str


def delete_spk(text: str) -> list[str]:
    """
    remove speakers
    :param text: text in format 'Speaker №: text'
    :return: list of words from text without word 'Speaker' and numbers
    """
    res = []
    for elem in text.split('\n'):
        res += elem.split(':')[1].strip().split()
    return res


def compare_spk_word(text: str) -> list[list[str]]:
    """
    definition of speaker-word pairs
    :param text: text in format 'Speaker №: text'
    :return: list with pair [speaker, word]
    """
    res = []
    text = text.split('\n')
    for elem in text:
        temp = elem.split(':')

        for word in temp[1].split():
            res.append([temp[0].split()[1], word])
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


def compare(orig: str, error: str) -> tuple[str, str]:
    """
    Compare of source files
    :param orig: reference text
    :param error: recognize text
    :return res_orig: reference text in format 'Speaker №, text, number of words of this speaker'
    :return res_error: recognize text in format ' Speaker №, text, number of words if the
    speaker differs from the reference'
    """

    orig_spk_word = compare_spk_word(orig)
    error_spk_word = compare_spk_word(error)
    indexes_res = diff_word_ind(delete_spk(orig), delete_spk(error))

    # matching speaker-word pairs in the original file and the recognized one
    res_orig = 'ref speaker:text:words count'
    res_error = 'result speaker:text:error words'
    speaker_old_orig = 0
    speaker_old_error = 0
    for element in indexes_res:
        speaker_new_orig = orig_spk_word[element[0]][0]
        speaker_new_error = error_spk_word[element[1]][0]
        if speaker_old_orig != speaker_new_orig:
            res_orig += f'\nSpeaker {orig_spk_word[element[0]][0]}:'
            res_error += f'\nSpeaker {error_spk_word[element[1]][0]}:'
            speaker_old_orig = speaker_new_orig
        if speaker_old_error != speaker_new_error:
            res_error += f'\nSpeaker {error_spk_word[element[1]][0]}:'
            res_orig += f'\nSpeaker {orig_spk_word[element[0]][0]}:'
            speaker_old_error = speaker_new_error
        res_orig += f'{orig_spk_word[element[0]][1]} '
        res_error += f'{error_spk_word[element[1]][1]} '
    return res_orig, res_error


def write(res_file: list, res_name: str) -> None:
    """
    Write output file
    :param res_file: list with result table strings
    :param res_name: path to output file
    """
    with open(res_name, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL, delimiter=',')
        for elem in res_file:
            writer.writerow(elem)


def result_count(orig: str, error: str) -> list:
    """
    Create output result
    :param orig: reference text in format 'Speaker №, text, number of words of this speaker'
    :param error: recognize text in format ' Speaker №, text, number of words if the speaker differs
    from the reference'
    :return: list with result table strings
    """
    orig = orig.split('\n')
    error = error.split('\n')
    result = []
    total_word = 0
    spk_error_word = 0

    for ind, elem in enumerate(orig):
        col_3 = ''
        col_6 = ''
        col_1, *col_2 = elem.split(':')
        col_4, *col_5 = error[ind].split(':')
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
    """
    orig_file: reference input file
    recognised_file: stt-recognise input file
    result_file: output result file
    """
    parser = argparse.ArgumentParser(
        description='compare reference and STT files for analise speaker error rate'
    )
    parser.add_argument('reference', type=str, help='Input reference file')
    parser.add_argument('recognized', type=str, help='Input recognized file')
    parser.add_argument('-r', '--result',
                        type=str,
                        default=None,
                        help='Output result file, default: None')
    args = parser.parse_args()

    # reading files
    with open(args.reference, 'r', encoding='utf-8') as orig:
        orig_str = orig.read()
    with open(args.recognized, 'r', encoding='utf-8') as recognized:
        recognized_str = recognized.read()
    orig_str = cleaning(orig_str)
    recognized_str = cleaning(recognized_str)
    res_orig, res_error = compare(orig_str, recognized_str)
    # compare(orig_str, recognized_str)
    res = result_count(res_orig, res_error)
    if args.result:
        write(res, args.result)


if __name__ == '__main__':
    main()
