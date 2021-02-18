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
        :headers: custom headers if you want ones
        Returns True if connection is ok
        Else returns False
        """

        api_login_url = 'https://api.ecoledirecte.com/v3/login.awp'
        unformatted_login = {
            'identifiant': username,
            'motdepasse': password,
            'acceptationCharte': True
        }

        self.response = self.request_post(api_login_url, unformatted_login)

        try:
            self.token = str(self.response['token'])
            self.eleve_id = str(self.response['data']['accounts'][0]['id'])
            self.api_notes_url = 'https://api.ecoledirecte.com/v3/eleves/' + self.eleve_id + '/notes.awp?verbe=get&'
        except Exception:
            raise LoginException('Please check your login ...')
            pass

    def request_post(self, url, unformatted_payload=None, headers=None):
        """
        Method to connect to the EcoleDirecte Api
        :url: url to connect
        :unformatted_payload: raw payload if None default one will be used (token)
        :headers: headers if None default will be used
        :return: raw data from the request
        """


        if headers is None:
            headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"}
        elif headers is not None:
            headers = headers

        if unformatted_payload is None:
            default_unformatted_payload = {
                'token': self.token
            }
        elif unformatted_payload is not None:
            default_unformatted_payload = unformatted_payload

        payload = {'data': json.dumps(default_unformatted_payload)}
        response = r('POST', url, data=payload, headers=headers).json()

        return response

    def fetch_notes(self):
        """
        Method to get notes from the API
        :return: Returns tuple with notes
        """

        response_notes = \
            self.request_post('https://api.ecoledirecte.com/v3/eleves/'
                              + self.eleve_id
                              + '/notes.awp?verbe=get&'
                              )
        raw_notes = response_notes['data']
        pop_list = ['idPeriode',
                    'codePeriode',
                    'annuel',
                    'examenBlanc',
                    'cloture',
                    'moyNbreJoursApresConseil']

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

    def format_notes(self):
        notes =self.fetch_notes()


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

    def get_homework(self, date):
        """
        Method to get the homework with the date
        :date: date format should be like this : yyyy-mm-dd
        :return:
        """

        response_homework = \
            self.request_post(
                'https://api.ecoledirecte.com/v3/eleves/'
                + self.eleve_id
                + '/cahierdetexte/'
                + date
                + '.awp?verbe=get&')


        return response_homework
