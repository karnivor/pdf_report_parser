import sys
import os
import PyPDF2
import json
import re
import zlib
import pandas as pd
import numpy as np

# TODO:
# -

# Notes:
# https://stackoverflow.com/questions/62136323/how-to-convert-pdf-document-to-json-using-python-script
# https://stackoverflow.com/questions/53608910/decompress-flatedecode-objects-in-pdf-in-python


##############################################################################

def fetch_key(df_in, coords):

    mask = (df_in.iloc[:, 0] == coords[0]) & (df_in.iloc[:, 1] == coords[1])

    if sum(mask) == 1:
        return df_in.loc[mask, 2].iloc[0]
    else:
        return ''

##############################################################################

def find_tag_coords(df_in, row_name):

    coords = []
    mask = df_in.iloc[:,2] == row_name
    coords.append(df_in.loc[mask, 0].iloc[0])
    coords.append(df_in.loc[mask, 1].iloc[0])

    return coords

##############################################################################

def find_col_coords(df_in, row_name):

    coords = find_tag_coords(df_in, row_name)

    mask = (df_in.iloc[:, 1] == coords[1]) & (df_in.iloc[:, 0] > coords[0])

    coord_arr = np.sort(df_in.loc[mask, 0].values)

    return coord_arr

##############################################################################

def find_value_coords(df_in, tag_name):

    if tag_name == 'P':
        row_name = 'P-R-T axes'
        ind = 0
    elif tag_name == 'R':
        row_name = 'P-R-T axes'
        ind = 1
    elif tag_name == 'T':
        row_name = 'P-R-T axes'
        ind = 2
    else:
        row_name = tag_name
        ind = 0

    coords = find_tag_coords(df_in, row_name)

    coord_list = find_col_coords(df_in, row_name)

    return_coords = [coord_list[ind], coords[1]]

    return return_coords

##############################################################################

def find_header_col(df_in):

    row_names = ['Vent. rate', 'PR interval', 'QRS duration', 'QT/QTc', 'P-R-T axes']

    col_numbers = []

    for name in row_names:
        col_numbers.append(df_in.loc[df_in.iloc[:,2] == name, 0].iloc[0])

    return int(np.median(np.array(col_numbers)))

##############################################################################

def dump_decoded_streams(path_reports):

    for file_name in os.listdir(path_reports):
        # print(os.path.join(path_reports, file_name))

        if file_name.endswith('.pdf'):
            full_file_name = os.path.join(path_reports, file_name)

            pdf = open(full_file_name, 'rb').read()
            stream = re.compile(b'.*?FlateDecode.*?stream(.*?)endstream', re.S)

            full_file_name_out = full_file_name[:-4] + '.txt'

            if os.path.exists(full_file_name_out):
                os.remove(full_file_name_out)

            for s in re.findall(stream, pdf):
                s = s.strip(b'\r\n')
                try:
                    file_h = open(full_file_name_out, 'a')
                    file_h.write(zlib.decompress(s).decode('UTF-8'))
                    file_h.close()

                except Exception as err:
                    print(err)


##############################################################################

def concat_texts(df_in):

    coords_tag = find_tag_coords(df_in, 'Vent. rate')
    coords_col = find_col_coords(df_in, 'Vent. rate')

    mask = (df_in.iloc[:, 0] == coords_col[2]) & (df_in.iloc[:, 1] <= coords_tag[1])

    coord_arr = np.sort(df_in.loc[mask, 1].values)[::-1]

    text = ''

    for coord, ind in zip(coord_arr, range(len(coord_arr))):
        text = text + df_in.loc[(df_in.iloc[: ,0] == coords_col[2]) & (df_in.iloc[:, 1] == coord), 2].iloc[0]\

        if ind < len(coord_arr) - 1:
            text = text + ';'

    return text


##############################################################################

def concat_texts_to_list(df_in, max_n_of_cols):

    coords_tag = find_tag_coords(df_in, 'Vent. rate')
    coords_col = find_col_coords(df_in, 'Vent. rate')

    mask = (df_in.iloc[:, 0] == coords_col[2]) & (df_in.iloc[:, 1] <= coords_tag[1])

    coord_arr = np.sort(df_in.loc[mask, 1].values)[::-1]

    texts_list = []

    for ind in range(max_n_of_cols):

        if ind < len(coord_arr):
            texts_list.append(df_in.loc[(df_in.iloc[: ,0] == coords_col[2]) & (df_in.iloc[:, 1] == coord_arr[ind]), 2].iloc[0])
        else:
            texts_list.append('')

    return texts_list

##############################################################################

def read_decoded_streams(path_reports, out_file_name):

    max_n_of_text_cols = 10

    title_row = ['tiedosto', 'nimi', 'hetu', 'aika', 'Ventilation rate', 'PR interval', 'QRS duration', 'QT', 'QTc', 'P', 'R', 'T']

    title_texts = []

    for ind in range(max_n_of_text_cols):
        title_texts.append('text_%d' % ind)

    title_row = title_row + title_texts

    rows = []

    for file_name in os.listdir(path_reports):
        # print(os.path.join(path_reports, file_name))

        if file_name.endswith('.txt'):
            row = []

            full_file_name = os.path.join(path_reports, file_name)

            file_h = open(full_file_name, 'r')
            stream = file_h.read()

            file_h.close()

            row.append(file_name)

            matches = re.findall('BT\s(\d+)\s(\d+)\sTd\s\((.*?)\)\sTj\sET', stream)

            df_matches = pd.DataFrame(matches)
            df_matches.iloc[:,0] = df_matches.iloc[:,0].astype(int)
            df_matches.iloc[:,1] = df_matches.iloc[:,1].astype(int)

            col_num = find_header_col(df_matches)

            row.append(fetch_key(df_matches, [450, 20030]))
            row.append(fetch_key(df_matches, [7750, 20030])[3:])
            row.append(fetch_key(df_matches, [11550, 20030]))
            row.append(fetch_key(df_matches, find_value_coords(df_matches, 'Vent. rate')))  # Vent. rate
            row.append(fetch_key(df_matches, find_value_coords(df_matches, 'PR interval')))  # PR interval
            row.append(fetch_key(df_matches, find_value_coords(df_matches, 'QRS duration')))  # QRS duration

            splitted = fetch_key(df_matches, find_value_coords(df_matches, 'QT/QTc')).split('/')

            row.append(splitted[0])
            row.append(splitted[1])

            row.append(fetch_key(df_matches, find_value_coords(df_matches, 'P')))
            row.append(fetch_key(df_matches, find_value_coords(df_matches, 'R')))
            row.append(fetch_key(df_matches, find_value_coords(df_matches, 'T')))
            # row.append(concat_texts(df_matches))
            row = row + concat_texts_to_list(df_matches, max_n_of_text_cols)

            rows.append(row)

    df_out = pd.DataFrame(rows, columns=title_row)

    df_out.to_excel(out_file_name, index=False)

##############################################################################

def parse_report(path_reports):

    for file_name in os.listdir(path_reports):
        # print(os.path.join(path_reports, file_name))

        if file_name.endswith('.pdf'):

            full_file_name = os.path.join(path_reports, file_name)

            read_pdf = PyPDF2.PdfFileReader(full_file_name)

            number_of_pages = read_pdf.getNumPages()

            for page_no in range(number_of_pages):

                page = read_pdf.getPage(page_no)

                page_content = page.extractText()
                data = json.dumps(page_content)
                formatj = json.loads(data)

##############################################################################

if __name__ == '__main__':

    # parse_report(sys.argv[1], sys.argv[2])

    dump_decoded_streams(sys.argv[1])
    read_decoded_streams(sys.argv[1], sys.argv[2])