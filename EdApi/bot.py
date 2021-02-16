import json

from requests import request as r

from EdApi.common.exceptions import LoginException


class EdBot:
    """
    A bot to connect to the EcoleDirecte Api with requests
    """

    def __init__(self, username, password):
        """
        Connect to the api with username and password
        :username:  username of user's account
        :password:  password of user's account

        Returns True if connection is ok
        Else returns False
        """
        api_login_url = 'https://api.ecoledirecte.com/v3/login.awp'
        unformatted_login = {
            'identifiant': username,
            'motdepasse': password,
            'acceptationCharte': True
        }

        payload = {'data': json.dumps(unformatted_login)}
        self.response = r('POST', api_login_url, data=payload).json()
        try:
            self.token = str(self.response['token'])
            self.eleve_id = str(self.response['data']['accounts'][0]['id'])
            self.api_notes_url = 'https://api.ecoledirecte.com/v3/eleves/' + self.eleve_id + '/notes.awp?verbe=get&'
        except Exception:
            raise LoginException('Please check your login ...')
            pass

    def fetch_notes(self):
        """
        Method to get notes from the API
        :return: Returns tuple with notes
        """
        unformatted_payload = {
            'token': self.token
        }
        payload = {'data': json.dumps(unformatted_payload)}
        response_notes = r('POST', self.api_notes_url, data=payload).json()
        raw_notes = response_notes['data']
        pop_list = ['idPeriode', 'codePeriode', 'annuel', 'examenBlanc', 'cloture', 'moyNbreJoursApresConseil']
        for j in range(0, 3):
            for i in range(0, len(pop_list)):
                raw_notes['periodes'][j].pop(pop_list[i])
                try:
                    raw_notes['periodes'][j]['ensembleMatieres'].pop('disciplinesSimulation')
                except KeyError:
                    pass

        trimestre_1 = raw_notes['periodes'][0]
        trimestre_2 = raw_notes['periodes'][1]
        trimestre_3 = raw_notes['periodes'][2]
        annee = raw_notes['periodes'][3]
        notes = raw_notes['notes']

        return trimestre_1, trimestre_2, trimestre_3, annee, notes

    def get_information(self):
        """
        Method that uses the login response to find information such as name email ...
        :return: information which is a dict
        """
        # TODO information.update({'NombreAnneesDansEtablissement':''})

        information = {}

        # Get the name
        information.update({'nom': self.response['data']['accounts'][0]['nom']})
        # Get the surname
        information.update({'prenom': self.response['data']['accounts'][0]['prenom']})
        # Get the name of the grade
        information.update({'classe': self.response['data']['accounts'][0]['profile']['classe']['libelle']})
        # Get the email and add it
        information.update({'email': self.response['data']['accounts'][0]['email']})
        # Add the EleveId
        information.update({'EleveId': self.eleve_id})
        # Get the name of the school
        information.update({'nomEtablissement': self.response['data']['accounts'][0]['nomEtablissement']})
        # Get the last connection
        information.update({'LastConnection': self.response['data']['accounts'][0]['lastConnexion']})
        # get the photo url /!\ user have to join it with the controller url
        information.update({'photoUrl': self.response['data']['accounts'][0]['profile']['photo']})

        return information


class dz:
    pass