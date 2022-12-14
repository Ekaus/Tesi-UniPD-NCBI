# -*- coding: utf-8 -*-
"""Tesi NCBI GitHub.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1B3EPaUb9d-fX8lhPaLxDv-XNvXFtVZVU

E' necessario eseguire installare il pacchetto Bio (se non già installato sul dispositivo) per poter effettuare le richieste al sistema Entrez.
"""

!pip install Bio

"""Il file CSV deve rispettare alcuni requisiti:

*   Nome: "Dataset.csv" (modificabile da codice)
*   Separatore: ";" (punto e virgola, modificabile da codice)
*   Colonna obbligatoria: "Specie" (che contiene i nomi delle specie, nome modificabile da codice)








"""

#Vengono importati tutti i pacchetti necessari
import numpy as np
import pandas as pd
import re
from google.colab import output as os

#Viene importato il file CSV contenente le specie. E' possibile cambiare il nome del file e il separatore utilizzato.
df = pd.read_csv('Dataset.csv', sep=";")

#Viene scansionata la lista e viene mostrata a schermo, utile a fini di debugging.
testDataset = df
for (id, row) in testDataset.iterrows():
  print(row.Specie)

pattern = re.compile("\s*\([a-z,A-Z]*\)\s*") #Spazio e testo tra parentesi

#Qui vanno riportati i template che si desidera utilizzare
#[{Abilitato per la ricerca : True/False}, {Nome della colonna}, {Stringa formattata per ricerca}]
templates = [
    [True, "Mitocondriale", "nucleotide", "\"{SPECIE}\"[Title/Abstract] mitochondrion genome"],
    [True, "Trascrittoma", "nucleotide", "TSA: \"{SPECIE}\" transcriptome shotgun assembly"],
    [True, "Nucleare", "genome", "\"{SPECIE}\"[orgn]"],
]

#Filtra i template selezionando soltanto quelli attivi, ovvero con primo valore "True"
templates = [tem for tem in templates if tem[0]]

"""Ricerca ed elaborazione risultati"""

#Importa il sottopacchetto Entrez
from Bio import Entrez
#Dati configurazione API
Entrez.email = "EMAIL@DOMINIO.IT"
Entrez.api_key = "APIKEYPERSONALE"

#Creazione file output
output = pd.DataFrame(columns=["Specie"])
for template in templates:
  output[template[1]] = []


#Ricerca iterativa per ogni specie
for (id, row) in testDataset.iterrows():
  risultati = [row.Specie]
  #Cerca tutti gli attributi selezionati tramite template precedentemente
  for template in templates:

    #Effettua la ricerca e verifica il numero di risultati
    query = template[3].format(SPECIE = row.Specie)
    handle = Entrez.esearch(db=template[2], retmax=10, term=query, idtype="acc")
    record = Entrez.read(handle)
    handle.close()

    #Se contiene testo tra parentesi e non ha trovato risultati, riprova senza parentesi
    if int(record["Count"]) == 0 and bool(re.search(pattern, row.Specie)) :
      query = template[3].format(SPECIE = re.sub("\s*\([a-z,A-Z]*\)\s*", " ", row.Specie))
      handle = Entrez.esearch(db=template[2], retmax=10, term=query, idtype="acc")
      record = Entrez.read(handle)
      print("Parentesi rimosse")
      handle.close()

    #Salva il numero di risultati restituiti
    risultati.append(int(record["Count"]))

  output.loc[len(output.index)] = risultati
  
  #Aggiorna la console e mostra il numero di specie elaborate rispetto al totale (es. 15/100, 503/9500)
  os.clear()
  print(len(output.index),"/",testDataset.shape[0])

#Converte i risultati numerici in valori booleani. Se si desidera mantenere l'informazione numerica, è necessario commentare le prime due righe.
column_names = output.select_dtypes(include=[np.number]).columns
output[column_names] = output[column_names].astype(bool)

#Mostra a schermo la tabella completa. Se non desiderato si può commentare la riga.
display(output)

#Salvataggio file output
output.to_csv('fileOutput.csv', index=False)