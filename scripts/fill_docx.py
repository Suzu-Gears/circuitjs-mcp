import os
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

def add_heading(doc, text, level=2):
    doc.add_heading(text, level=level)

def add_paragraph(doc, text):
    doc.add_paragraph(text)

def add_table(doc, rows):
    table = doc.add_table(rows=1, cols=len(rows[0]))
    hdr_cells = table.rows[0].cells
    for i, val in enumerate(rows[0]):
        hdr_cells[i].text = val
    for row in rows[1:]:
        cells = table.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = val
    return table

def add_image(doc, path, caption=None):
    if os.path.exists(path):
        doc.add_picture(path, width=Inches(5))
        if caption:
            p = doc.paragraphs[-1]
            p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            doc.add_paragraph(caption)

def add_link(doc, url):
    p = doc.add_paragraph()
    p.add_run('Відкрити схему у Falstad → ')
    p.add_run(url)

# Paths
original_path = '/Users/vladimirhohlov/Downloads/Хохлов 381.docx'
backup_path = '/Users/vladimirhohlov/Downloads/Хохлов 381_backup_script.docx'
# Create backup
import shutil
shutil.copyfile(original_path, backup_path)

# Load document

doc = Document(original_path)

# Task definitions (title, description, truth table, screenshot, link)

tasks = [
    {
        'title': 'сегмент a',
        'heading': 'Результати завдання 1 (сегмент a)',
        'description': 'Таблиця істинності для сегмента a (верхній горизонтальний сегмент) згідно таблиці 1.',
        'truth': [
            ['BCD (деc)', 'a'],
            ['0', '1'], ['1', '0'], ['2', '1'], ['3', '1'], ['4', '0'], ['5', '1'], ['6', '1'], ['7', '1'], ['8', '1'], ['9', '1']
        ],
        'screenshot': '/tmp/seg_task1.png',
        'link': 'https://www.falstad.com/circuit/circuitjs.html?ctz=CQAgzCAMB0l3BWK0AsBGATGMCME48B2DANjwA4M0IFIQlb6BTAWjTQCg0FCRzy6WDCDTwQQqCF51IHAO4gSAkGxJ1CkFCrRqo8xWGGq6JBCW27ZChOS3HFkchZkcAkouX2ldNpkkwGNwMjHRNDbT8ZaED3GztQ+lsI4SiY+jBzewQM5P9o+g4AGQ8fBO9tJJSQADMAQwAbAGcmej1iknCvTrRKkRqG5tbZYrjnRPjetH6mlqRh9MyE7MXeujqZof1lsbNSyy4EKdFiFQwtY+Ezvq1A7imiTKuH8XOQG4K7kDwMJxYnn5e11aCAOR0gVz+53BWiuU3eIM+-B8VyRgLhwNBUiSkKxMNeWjoCMOfE6KPCsLeGO46iSOichEqOiBt0YxCcdKkAKo5im5kJBxMsKUiiu3L6DA+jBIJw50suTPRLMJfg5h3lPOBksJwtVwrFvKpjBQJHOwuNMIVlMCCjFKBMjjeLhtJreThILpQTis4F0Hs9igJ+hQZj4JiZym9dvpwkIuE5egUon4pyhyZYdoTIkcyNTPhD3tELpxhbsJwLkBDxYrmWT3t2O10LDwfP0al+ZQdLAjrcrZUrLu9GniuiHKn9dZyvmE2y7Xq22PY0+xZdb3T8HSM+dbnkXJTHTqzTJYMsgRZXCmIOc5Plr+kIwpx99+t4U5CPKKPL74RZRRa-eD8HEAKMf9GyeRsvzZFNOWfA9CHvaD4JrA9KDsFEIW7T5CEnK5sPMCl4X0URO1hOBnznaxJ2TS8VEgjAb3pB9IKYpw3xrCi+E-Vi-w48geK+QD-0EpxmwYzNRNo9kyMkzNiPIrNKy-cgThxZSQIPb4r00lRzy+B9wN+XTRHfKEj10ttaPUAEuzg6zlCQyzMwcmy+AwlC3L4FTu2sZdhG048Un0fyTmbQzAoUUKdOEYzMiMzQr1EDN0w4ggjCeb593ElA0K0PBsrHXjm2g8givTFD-VUirx30AQr1qzLBzjR8muqxNIFJKFOi3CLsSebEByCnDcsnAbXzTFE026vgkpRJKpsIDLH0W0apHyx81pW0xMhdQgNsDC89qkZb9qOowXTwEaTou7bcv6k6NxUENbDzFtXzm8x+F+KbPsenl2s3V6sy6v7PHmzQCqkFqONjIx-VsX5WumhGRLWxG8rsf1Ep8RHyjK0NsZQuBMpKzIM29EnMtShqgsWjMkwRg8MAhUUIRWjAVNFFSVsMK8ed+zMMl+K5Bf5yMTLeI8VvNaDpZYFa1WghWWCmiQcVVxGfivTXqYUQwha0PWIe9MAEJxE3SYPFBma0K2MY4lAOZtlSya2ejFbd5LMxQUqrm92LwreCrfYq3S7SvMOooFprhaazDiTFNWmQIjFdfBs20+88RK1FRTGZImFOzjqYwEA4W-GTlkplIHLxBdCvJWLsCDd0euiSmWga47tErQbx19b77vCM+YNHhtkNW6DcabbTIrIxmm2ktn-QwEW4XFqX3W1uFtaN-EH2YVK3ezn74+VCPom1Yv3f6ybdxPV+Xf77Pu-F8B7KfCKlejF3r-n-AHfAZgAAXvTIR9D74QqkfSB+Er6Awsi5HA6ko5ILABnA8qC7DKAwLnTM2DkLiELgeUYAU3ilVDmQ4Q2UwpexDpQi+5l+w2yLFLZhNtJYnXQDdcQXMTrszOjCVm91gb0EAlNJWIYRbK0AQ+CRHswZ23oB7RGuBsZOFtkbIMEJ-SG09sbay-p1YcVxhmB2sNLbOzoObHW4BTYZm1njSMyhuDRUgDKOM5YTikTcQHUQoooSwnyt6Z4TwELUEBt8Jw-x2QAnJlgrQqJMAoXJPE8Iu5ByVC0AyKEJ08KAlydfcGVwu5fhHoCUpmcoxlIdLpDIghm4mBOiXS4Bs-AqzrjCD0HExSiiZC7V8RMOT1TQIEu8GUOQLWim7QcoThQOV0k+EQszhTzTGW7BJUyaoDPyr484IyLyMnMFk8Q4RYmCHCEciQg4cjjOuZEO82zZnbPBo1aKsy4zzPBuM8GfSpAqlmX4RGNFxluxWjDeMczAoACUswyBEFMmFkAgA'
    },
    {
        'title': 'сегмент c',
        'heading': 'Результати завдання 2 (сегмент c)',
        'description': 'Таблиця істинності для сегмента c (верхній правий вертикальний сегмент) згідно варіанту 11. Для цифри 2 результат 0, для цифр 5 і 6 – 1.',
        'truth': [
            ['BCD (деc)', 'c'],
            ['0', '1'], ['1', '1'], ['2', '0'], ['3', '1'], ['4', '1'], ['5', '1'], ['6', '1'], ['7', '1'], ['8', '1'], ['9', '1']
        ],
        'screenshot': '/tmp/seg_task2.png',
        'link': 'https://www.falstad.com/circuit/circuitjs.html?ctz=CQAgzCAMB0l3BWK0AsBGATGMCME48B2DANjwA4M0IFIQlb6BTAWjTQCg0FCRzy6WDCDTwQQqCF51IHAO4gSAkGxJ1CkFCrRqo8xWGGq6JBCW27ZChOS3HFkchZkcAkouX2ldNpkkwGNwMjHRNDbT8ZaED3GztQ+lsI4SiY+jBzewQM5P9o+g4AGQ8fBO9tJJSQADMAQwAbAGcmej1iknCvTrRKkRqG5tbZYrjnRPjetH6mlqRh9MyE7MXeujqZof1lsbNSyy4EKdFiFQwtY+Ezvq1A7imiTKuH8XOQG4K7kDwMJxYnn5e11aCAOR0gVz+53BWiuU3eIM+-B8VyRgLhwNBUiSkKxMNeWjoCMOfE6KPCsLeGO46iSOichEqOiBt0YxCcdKkAKo5im5kJBxMsKUiiu3L6DA+jBIJw50suTPRLMJfg5h3lPOBksJwtVwrFvKpjBQJHOwuNMIVlMCCjFKBMjjeLhtJreThILpQTis4F0Hs9igJ+hQZj4JiZym9dvpwkIuE5egUon4pyhyZYdoTIkcyNTPhD3tELpxhbsJwLkBDxYrmWT3t2O10LDwfP0al+ZQdLAjrcrZUrLu9GniuiHKn9dZyvmE2y7Xq22PY0+xZdb3T8HSM+dbnkXJTHTqzTJYMsgRZXCmIOc5Plr+kIwpx99+t4U5CPKKPL74RZRRa-eD8HEAKMf9GyeRsvzZFNOWfA9CHvaD4JrA9KDsFEIW7T5CEnK5sPMCl4X0URO1hOBnznaxJ2TS8VEgjAb3pB9IKYpw3xrCi+E-Vi-w48geK+QD-0EpxmwYzNRNo9kyMkzNiPIrNKy-cgThxZSQIPb4r00lRzy+B9wN+XTRHfKEj10ttaPUAEuzg6zlCQyzMwcmy+AwlC3L4FTu2sZdhG048Un0fyTmbQzAoUUKdOEYzMiMzQr1EDN0w4ggjCeb593ElA0K0PBsrHXjm2g8givTFD-VUirx30AQr1qzLBzjR8muqxNIFJKFOi3CLsSebEByCnDcsnAbXzTFE026vgkpRJKpsIDLH0W0apHyx81pW0xMhdQgNsDC89qkZb9qOowXTwEaTou7bcv6k6NxUENbDzFtXzm8x+F+KbPsenl2s3V6sy6v7PHmzQCqkFqONjIx-VsX5WumhGRLWxG8rsf1Ep8RHyjK0NsZQuBMpKzIM29EnMtShqgsWjMkwRg8MAhUUIRWjAVNFFSVsMK8ed+zMMl+K5Bf5yMTLeI8VvNaDpZYFa1WghWWCmiQcVVxGfivTXqYUQwha0PWIe9MAEJxE3SYPFBma0K2MY4lAOZtlSya2ejFbd5LMxQUqrm92LwreCrfYq3S7SvMOooFprhaazDiTFNWmQIjFdfBs20+88RK1FRTGZImFOzjqYwEA4W-GTlkplIHLxBdCvJWLsCDd0euiSmWga47tErQbx19b77vCM+YNHhtkNW6DcabbTIrIxmm2ktn-QwEW4XFqX3W1uFtaN-EH2YVK3ezn74+VCPom1Yv3f6ybcxPV+Xf77Pu-F8B7KfCKlejF3r-n-AHfAZgAAXvTIR9D74QqkfSB+Er6Awsi5HA6ko5ILABnA8qC7DKAwLnTM2DkLiELgeUYAU3ilVDmQ4Q2UwpexDpQi+5l+w2yLFLZhNtJYnXQDdcQXMTrszOjCVm91gb0EAlNJWIYRbK0AQ+CRHswZ23oB7RGuBsZOFtkbIMEJ-SG09sbay-p1YcVxhmB2sNLbOzoObHW4BTYZm1njSMyhuDRUgDKOM5YTikTcQHUQoooSwnyt6Z4TwELUEBt8Jw-x2QAnJlgrQqJMAoXJPE8Iu5ByVC0AyKEJ08KAlydfcGVwu5fhHoCUpmcoxlIdLpDIghm4mBOiXS4Bs-AqzrjCD0HExSiiZC7V8RMOT1TQIEu8GUOQLWim7QcoThQOV0k+EQszhTzTGW7BJUyaoDPyr484IyLyMnMFk8Q4RYmCHCEciQg4cjjOuZEO82zZnbPBo1aKsy4zzPBuM8GfSpAqlmX4RGNFxluxWjDeMczAoACUswyBEFMmFkAgA'
    },
    {
        'title': 'сегменти a та d',
        'heading': 'Результати завдання 3 (спільна схема сегментів a та d)',
        'description': 'Таблиця істинності для одночасного отримання сегментів a (верхній горизонтальний) та d (нижній горизонтальний) згідно варіанту 11.',
        'truth': [
            ['BCD (деc)', 'a', 'd'],
            ['0', '1', '1'], ['1', '0', '0'], ['2', '1', '1'], ['3', '1', '1'], ['4', '0', '0'],
            ['5', '1', '1'], ['6', '1', '1'], ['7', '1', '0'], ['8', '1', '1'], ['9', '1', '1']
        ],
        'screenshot': '/tmp/seg_task3.png',
        'link': 'https://www.falstad.com/circuit/circuitjs.html?ctz=CQAgzCAMB0l3BWK0AsBGATGMCME48B2DANjwA4M0IFIQlb6BTAWjTQCg0FCRzy6WDCDTwQQqCF51IHAO4gSAkGxJ1CkFCrRqo8xWGGq6JBCW27ZChOS3HFkchZkcAkouX2ldNpkkwGNwMjHRNDbT8ZaED3GztQ+lsI4SiY+jBzewQM5P9o+g4AGQ8fBO9tJJSQADMAQwAbAGcmej1iknCvTrRKkRqG5tbZYrjnRPjetH6mlqRh9MyE7MXeujqZof1lsbNSyy4EKdFiFQwtY+Ezvq1A7imiTKuH8XOQG4K7kDwMJxYnn5e11aCAOR0gVz+53BWiuU3eIM+-B8VyRgLhwNBUiSkKxMNeWjoCMOfE6KPCsLeGO46iSOichEqOiBt0YxCcdKkAKo5im5kJBxMsKUiiu3L6DA+jBIJw50suTPRLMJfg5h3lPOBksJwtVwrFvKpjBQJHOwuNMIVlMCCjFKBMjjeLhtJreThILpQTis4F0Hs9igJ+hQZj4JiZym9dvpwkIuE5egUon4pyhyZYdoTIkcyNTPhD3tELpxhbsJwLkBDxYrmWT3t2O10LDwfP0al+ZQdLAjrcrZUrLu9GniuiHKn9dZyvmE2y7Xq22PY0+xZdb3T8HSM+dbnkXJTHTqzTJYMsgRZXCmIOc5Plr+kIwpx99+t4U5CPKKPL74RZRRa-eD8HEAKMf9GyeRsvzZFNOWfA9CHvaD4JrA9KDsFEIW7T5CEnK5sPMCl4X0URO1hOBnznaxJ2TS8VEgjAb3pB9IKYpw3xrCi+E-Vi-w48geK+QD-0EpxmwYzNRNo9kyMkzNiPIrNKy-cgThxZSQIPb4r00lRzy+B9wN+XTRHfKEj10ttaPUAEuzg6zlCQyzMwcmy+AwlC3L4FTu2sZdhG048Un0fyTmbQzAoUUKdOEYzMiMzQr1EDN0w4ggjCeb593ElA0K0PBsrHXjm2g8givTFD-VUirx30AQr1qzLBzjR8muqxNIFJKFOi3CLsSebEByCnDcsnAbXzTFE026vgkpRJKpsIDLH0W0apHyx81pW0xMhdQgNsDC89qkZb9qOowXTwEaTou7bcv6k6NxUENbDzFtXzm8x+F+KbPsenl2s3V6sy6v7PHmzQCqkFqONjIx-VsX5WumhGRLWxG8rsf1Ep8RHyjK0NsZQuBMpKzIM29EnMtShqgsWjMkwRg8MAhUUIRWjAVNFFSVsMK8ed+zMMl+K5Bf5yMTLeI8VvNaDpZYFa1WghWWCmiQcVVxGfivTXqYUQwha0PWIe9MAEJxE3SYPFBma0K2MY4lAOZtlSya2ejFbd5LMxQUqrm92LwreCrfYq3S7SvMOooFprhaazDiTFNWmQIjFdfBs20+88RK1FRTGZImFOzjqYwEA4W-GTlkplIHLxBdCvJWLsCDd0euiSmWga47tErQbx19b77vCM+YNHhtkNW6DcabbTIrIxmm2ktn-QwEW4XFqX3W1uFtaN-EH2YVK3ezn74+VCPom1Yv3f6ybcxPV+Xf77Pu-F8B7KfCKlejF3r-n-AHfAZgAAXvTIR9D74QqkfSB+Er6Awsi5HA6ko5ILABnA8qC7DKAwLnTM2DkLiELgeUYAU3ilVDmQ4Q2UwpexDpQi+5l+w2yLFLZhNtJYnXQDdcQXMTrszOjCVm91gb0EAlNJWIYRbK0AQ+CRHswZ23oB7RGuBsZOFtkbIMEJ-SG09sbay-p1YcVxhmB2sNLbOzoObHW4BTYZm1njSMyhuDRUgDKOM5YTikTcQHUQoooSwnyt6Z4TwELUEBt8Jw-x2QAnJlgrQqJMAoXJPE8Iu5ByVC0AyKEJ08KAlydfcGVwu5fhHoCUpmcoxlIdLpDIghm4mBOiXS4Bs-AqzrjCD0HExSiiZC7V8RMOT1TQIEu8GUOQLWim7QcoThQOV0k+EQszhTzTGW7BJUyaoDPyr484IyLyMnMFk8Q4RYmCHCEciQg4cjjOuZEO82zZnbPBo1aKsy4zzPBuM8GfSpAqlmX4RGNFxluxWjDeMczAoACVwBE0sVMmFcAgA'
    },
    {
        'title': 'варіант 381‑36‑LOVE',
        'heading': 'Результати завдання 4 (варіант 381‑36‑LOVE)',
        'description': 'Таблиця істинності для послідовності 3, 8, 1, –, 3, 6, –, L, O, V, E. Дефіс означає «не важливо».',
        'truth': [
            ['Символ', 'a', 'b', 'c', 'd', 'e', 'f', 'g'],
            ['3', '1', '1', '1', '1', '0', '0', '1'],
            ['8', '1', '1', '1', '1', '1', '1', '1'],
            ['1', '0', '1', '1', '0', '0', '0', '0'],
            ['–', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
            ['3', '1', '1', '1', '1', '0', '0', '1'],
            ['6', '1', '0', '1', '1', '1', '1', '1'],
            ['–', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
            ['L', '0', '0', '0', '1', '1', '1', '0'],
            ['O', '1', '1', '1', '1', '1', '1', '0'],
            ['V', '0', '0', '1', '1', '1', '0', '0'],
            ['E', '1', '0', '0', '1', '1', '1', '1']
        ],
        'extra_paragraphs': [
            '- L: відображається лише ліві вертикальні сегменти (f, e) та нижній (d).',
            '- O: повний 0‑підпис, аналогічно цифрі 0.',
            '- V: у простій 7‑сегментній реалізації часто використовується комбінація сегментів c, d, e (правий нижній, нижній, лівий нижній).',
            '- E: стандартне відображення букви E зі ввімкненими сегментами a, d, e, f, g.'
        ],
        'screenshot': '/tmp/seg_task4.png',
        'link': 'https://www.falstad.com/circuit/circuitjs.html?ctz=CQAgzCAMB0l3BWK0AsBGATGMCME48B2DANjwA4M0IFIQlb6BTAWjTQCg0FCRzy6WDCDTwQQqCF51IHAO4gSAkGxJ1CkFCrRqo8xWGGq6JBCW27ZChOS3HFkchZkcAkouX2ldNpkkwGNwMjHRNDbT8ZaED3GztQ+lsI4SiY+jBzewQM5P9o+g4AGQ8fBO9tJJSQADMAQwAbAGcmej1iknCvTrRKkRqG5tbZYrjnRPjetH6mlqRh9MyE7MXeujqZof1lsbNSyy4EKdFiFQwtY+Ezvq1A7imiTKuH8XOQG4K7kDwMJxYnn5e11aCAOR0gVz+53BWiuU3eIM+-B8VyRgLhwNBUiSkKxMNeWjoCMOfE6KPCsLeGO46iSOichEqOiBt0YxCcdKkAKo5im5kJBxMsKUiiu3L6DA+jBIJw50suTPRLMJfg5h3lPOBksJwtVwrFvKpjBQJHOwuNMIVlMCCjFKBMjjeLhtJreThILpQTis4F0Hs9igJ+hQZj4JiZym9dvpwkIuE5egUon4pyhyZYdoTIkcyNTPhD3tELpxhbsJwLkBDxYrmWT3t2O10LDwfP0al+ZQdLAjrcrZUrLu9GniuiHKn9dZyvmE2y7Xq22PY0+xZdb3T8HSM+dbnkXJTHTqzTJYMsgRZXCmIOc5Plr+kIwpx99+t4U5CPKKPL74RZRRa-eD8HEAKMf9GyeRsvzZFNOWfA9CHvaD4JrA9KDsFEIW7T5CEnK5sPMCl4X0URO1hOBnznaxJ2TS8VEgjAb3pB9IKYpw3xrCi+E-Vi-w48geK+QD-0EpxmwYzNRNo9kyMkzNiPIrNKy-cgThxZSQIPb4r00lRzy+B9wN+XTRHfKEj10ttaPUAEuzg6zlCQyzMwcmy+AwlC3L4FTu2sZdhG048Un0fyTmbQzAoUUKdOEYzMiMzQr1EDN0w4ggjCeb593ElA0K0PBsrHXjm2g8givTFD-VUirx30AQr1qzLBzjR8muqxNIFJKFOi3CLsSebEByCnDcsnAbXzTFE026vgkpRJKpsIDLH0W0apHyx81pW0xMhdQgNsDC89qkZb9qOowXTwEaTou7bcv6k6NxUENbDzFtXzm8x+F+KbPsenl2s3V6sy6v7PHmzQCqkFqONjIx-VsX5WumhGRLWxG8rsf1Ep8RHyjK0NsZQuBMpKzIM29EnMtShqgsWjMkwRg8MAhUUIRWjAVNFFSVsMK8ed+zMMl+K5Bf5yMTLeI8VvNaDpZYFa1WghWWCmiQcVVxGfivTXqYUQwha0PWIe9MAEJxE3SYPFBma0K2MY4lAOZtlSya2ejFbd5LMxQUqrm92LwreCrfYq3S7SvMOooFprhaazDiTFNWmQIjFdfBs20+88RK1FRTGZImFOzjqYwEA4W-GTlkplIHLxBdCvJWLsCDd0euiSmWga47tErQbx19b77vCM+YNHhtkNW6DcabbTIrIxmm2ktn-QwEW4XFqX3W1uFtaN-EH2YVK3ezn74+VCPom1Yv3f6ybcxPV+Xf77Pu-F8B7KfCKlejF3r-n-AHfAZgAAXvTIR9D74QqkfSB+Er6Awsi5HA6ko5ILABnA8qC7DKAwLnTM2DkLiELgeUYAU3ilVDmQ4Q2UwpexDpQi+5l+w2yLFLZhNtJYnXQDdcQXMTrszOjCVm91gb0EAlNJWIYRbK0AQ+CRHswZ23oB7RGuBsZOFtkbIMEJ-SG09sbay-p1YcVxhmB2sNLbOzoObHW4BTYZm1njSMyhuDRUgDKOM5YTikTcQHUQoooSwnyt6Z4TwELUEBt8Jw-x2QAnJlgrQqJMAoXJPE8Iu5ByVC0AyKEJ08KAlydfcGVwu5fhHoCUpmcoxlIdLpDIghm4mBOiXS4Bs-AqzrjCD0HExSiiZC7V8RMOT1TQIEu8GUOQLWim7QcoThQOV0k+EQszhTzTGW7BJUyaoDPyr484IyLyMnMFk8Q4RYmCHCEciQg4cjjOuZEO82zZnbPBo1aKsy4zzPBuM8GfSpAqlmX4RGNFxluxWjDeMczAoACUswyBEFMmFkAgA'
    }
]

# Insert each task's results sequentially
for task in tasks:
    add_heading(doc, task['heading'], level=2)
    add_paragraph(doc, task['description'])
    add_table(doc, task['truth'])
    add_image(doc, task['screenshot'], caption=f'Скріншот схеми для {task["title"]}')
    # add_link(doc, task['link'])  # Links omitted per Falstad rules
    if task.get('extra_paragraphs'):
        add_paragraph(doc, 'Особливості відображення букв:')
        for p in task['extra_paragraphs']:
            add_paragraph(doc, p)

answers = [
    ('Що називається перетворювачем коду?', 'Перетворювач коду – це електрична схема, яка за заданим вхідним бінарним кодом генерує сигнали для семисегментного індикатора.'),
    ('Яке призначення перетворювача коду?', 'Перетворювач коду застосовується для візуального відображення чисел чи символів на індикаторі, спрощуючи інтерпретацію бінарних даних.'),
    ('Як влаштований Код Грея?', 'Код Грея – це бінарний код, у якому два послідовних числа differ by only one bit; переходи між числами здійснюються зміною лише одного бітa.'),
    ('Які недоліки присутні у коді Грея?', 'Недоліком є складність прямого перетворення у звичайний двійковий код і нелінійна залежність бітів, що ускладнює апаратну реалізацію.')
]

for i, p in enumerate(doc.paragraphs):
    if 'Контрольні питання' in p.text:
        insert_idx = i + 1
        break
else:
    insert_idx = len(doc.paragraphs)

for q, a in answers:
    doc.paragraphs.insert(insert_idx, doc.add_paragraph(q))
    doc.paragraphs.insert(insert_idx+1, doc.add_paragraph(a))
    insert_idx += 2

output_path = original_path
doc.save(output_path)
print('Document updated and saved with inserted results.')