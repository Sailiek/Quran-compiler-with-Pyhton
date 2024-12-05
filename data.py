from bs4 import BeautifulSoup
import requests
import pandas as pd
from google.colab import files
import json
##
url='https://www.altafsir.com/Tafasir.asp?tMadhNo=0&tTafsirNo=74&tSoraNo=1&tAyahNo=1&tDisplay=yes&UserProfile=0&LanguageId=2'
header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

page = requests.get(url,headers=header)

soup = BeautifulSoup(page.text,'html.parser')
soup
##
tafsir_content = soup.find('font', class_='TextResultEnglish')
tafsir_content.text.strip()
##
def scrape_tafsir(sora_no, ayah_no):
    url = f'https://www.altafsir.com/Tafasir.asp?tMadhNo=0&tTafsirNo=74&tSoraNo={sora_no}&tAyahNo={ayah_no}&tDisplay=yes&UserProfile=0&LanguageId=2'
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(page.text,'html.parser')
        tafsir_content = soup.find('font', class_='TextResultEnglish')
        tafsir_text = tafsir_content.text.strip()
    return tafsir_text

def scrape_surah(sora_no,num_ayat):
    data=[]
    for i in range(1,num_ayat+1):
        aya = scrape_tafsir(sora_no,i)
        data.append({
            'name':sora_no,
            'tafsir':aya,
        })
    return data


def scrap_evrything():
       
    num_ayat_per_surah = {
    1: 7, 2: 286, 3: 200, 4: 176, 5: 120, 6: 165, 7: 206, 8: 75, 9: 129, 10: 109,
    11: 123, 12: 111, 13: 43, 14: 52, 15: 99, 16: 128, 17: 111, 18: 110, 19: 98, 20: 135,
    21: 112, 22: 78, 23: 118, 24: 64, 25: 77, 26: 227, 27: 93, 28: 88, 29: 69, 30: 60,
    31: 34, 32: 30, 33: 73, 34: 54, 35: 45, 36: 83, 37: 182, 38: 88, 39: 75, 40: 85,
    41: 54, 42: 53, 43: 89, 44: 59, 45: 37, 46: 35, 47: 38, 48: 29, 49: 18, 50: 45,
    51: 60, 52: 49, 53: 62, 54: 55, 55: 78, 56: 96, 57: 29, 58: 22, 59: 24, 60: 13,
    61: 14, 62: 11, 63: 11, 64: 18, 65: 12, 66: 12, 67: 30, 68: 52, 69: 52, 70: 44,
    71: 28, 72: 28, 73: 20, 74: 56, 75: 40, 76: 31, 77: 50, 78: 40, 79: 46, 80: 42,
    81: 29, 82: 19, 83: 36, 84: 25, 85: 22, 86: 17, 87: 19, 88: 26, 89: 30, 90: 20,
    91: 15, 92: 21, 93: 11, 94: 8, 95: 8, 96: 19, 97: 5, 98: 8, 99: 8, 100: 11,
    101: 11, 102: 8, 103: 3, 104: 9, 105: 5, 106: 4, 107: 7, 108: 3, 109: 6, 110: 3,
    111: 5, 112: 4, 113: 5, 114: 6
    }
    all_surahs_data = []
    for i in range(1,115):
        num_ayat=num_ayat_per_surah[i] 
        data=scrape_surah(i,num_ayat)
        all_surahs_data.append(data)
    return all_surahs_data
        
        
        
        
        

