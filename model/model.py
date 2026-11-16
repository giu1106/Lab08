from database.distributore_DAO import DistributoreDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._distributori = None
        self.load_distributori()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        self._distributori = DistributoreDAO.get_distributori()

    def get_prezzo_medio(self, mese: int):
        """
        Calcola, per ogni distributore, il prezzo medio al litro per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome del distributore, media), es. (Distributore A, 1.789)
        """
        if self._distributori is None:
            return None

        risultati = []
        for distributore in self._distributori:
            prezzi_distributore = distributore.get_prezzi()
            if prezzi_distributore is not None:
                prezzi_mese = [p.prezzo_litro for p in prezzi_distributore if p.data.month == mese]
                if len(prezzi_mese) > 0:
                    media = sum(prezzi_mese) / len(prezzi_mese)
                    risultati.append((distributore.nome, media))
        return risultati

    def get_sequenza_ottima(self, mese: int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, prezzi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione """
        if giorno > 7:
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = list(sequenza_parziale)
            return

        for id_dist, lista_prezzi in prezzi_settimana.items():

            costo_giorno = lista_prezzi[giorno - 1] * 100

            if ultimo_distributore is not None and ultimo_distributore != id_dist:
                costo_giorno += 5

            if self.__costo_ottimo == -1 or (costo_corrente + costo_giorno) < self.__costo_ottimo:
                sequenza_parziale.append(id_dist)
                self.__ricorsione(
                    sequenza_parziale,
                    giorno + 1,
                    id_dist,
                    costo_corrente + costo_giorno,
                    prezzi_settimana
                )

                sequenza_parziale.pop()

    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        prezzi_settimana = {}
        if self._distributori is not None:
            for distributore in self._distributori:
                prezzi_dist = distributore.get_prezzi()
                if prezzi_dist is not None:
                    prezzi_7_giorni = [
                        p for p in prezzi_dist
                        if p.data.month == mese and 1 <= p.data.day <= 7
                    ]
                    prezzi_7_giorni.sort(key=lambda p: p.data)
                    prezzi_settimana[distributore.id] = [p.prezzo_litro for p in prezzi_7_giorni]
        return prezzi_settimana