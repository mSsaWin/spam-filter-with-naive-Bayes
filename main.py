import easyimap
import re
import pandas as pd
from collections import Counter

def adjective_filter(words):
  ends = ['ая', 'яя', 'ой', 'ей', 'ую', 'юю', 'ый', 'ий', 'ого', 'его', 'ому', 'ему', 'ым', 'им', 'ом', 'ем', 'ое', 'ее', 'ые', 'ие', 'ых', 'их', 'ыми','ими' ]
  for i in words:
    if i[:-2] in ends or i[:-3] in ends:
      words.remove(i)
  return words

def parseInCSV():
  server = "imap.yandex.ru"
  login = "******"
  password = "******"
  imap = easyimap.connect(server, login, password, mailbox='&BCEEPwQwBDw-')
  mail_list = imap.listids(limit=30)
  
  spam_mails = []

  for i in mail_list:
    email = imap.mail(i)
    spam_mails.append(
      {
      "Words":adjective_filter([word for word in re.findall(r'[а-яА-Я]{5,}', email.body)]),
      "Key": 1
      }
    )
  
  imap.change_mailbox("INBOX")
  mail_list = imap.listids(limit=30)
  
  ham_mails = []
  
  for i in mail_list:
    email = imap.mail(i)
    
    ham_mails.append(
      {
      "Words":adjective_filter([word for word in re.findall(r'[а-яА-Я]{5,}', email.body)]),
      "Key": 0
      }
    )

  frame = pd.DataFrame(ham_mails+spam_mails)
  frame.to_csv('mails.csv', encoding='utf-8', index=False)
  
  return transformToList(spam_mails), ham_mails, spam_mails

def transformToList(listOfDict):
  spam_words = []
  for dict in listOfDict:
    for word in dict["Words"]:
      spam_words.append(word)

  return spam_words

def findIndicator(spam_words):
  return Counter(spam_words).most_common(7)


def naive_bayes(massage, spam_indicators, ham_mails, spam_mails):
  meeting_indicators = []
  count = 0
  for word in spam_indicators:
    if word[0] in massage:
      meeting_indicators.append(word[0])
      
  if len(meeting_indicators) == 1:
    for dict in spam_mails:
      if meeting_indicators[0] in dict["Words"]:
        count += 1
    P_spam = count/len(spam_mails)

    count = 0
    for dict in ham_mails:
      if meeting_indicators[0] in dict["Words"]:
        count += 1
    P_ham = count/len(ham_mails)

    P = P_spam/(P_spam+P_ham)
    return P

  else:
    k = 1
    P_spam = 1
    P_ham = 1
    count = 0

    for word in meeting_indicators:
      for dict in spam_mails:
        if word in dict["Words"]:
          count += 1
      P_spam*=((k+count)/(2*k+len(spam_mails)))

    count = 0

    for word in meeting_indicators:
      for dict in ham_mails:
        if word in dict["Words"]:
          count += 1
      P_ham*=((k+count)/(2*k+len(ham_mails)))

    P = P_spam/(P_spam+P_ham)
    return P 


def main():
  spam_words, ham_mails, spam_mails = parseInCSV()
  spam_indicators = findIndicator(spam_words)
  print(spam_indicators)
  massanges = ['резюме получается как письмо на сайте','покупатьактивно что-то','группа активно пыталась сделать копию заказа','мы получили ваше письмо','тут наверное нет спама']
  for sentence in massanges:
    P = naive_bayes(sentence, spam_indicators, ham_mails, spam_mails)
    print(f"Верояность того, что письмо '{sentence}' является спамом с вероятностью =", P)

if __name__ == '__main__':
  main()