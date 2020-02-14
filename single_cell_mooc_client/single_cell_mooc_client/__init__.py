import ipywidgets as widgets
import requests
from IPython.display import clear_output, display, Javascript

class Submission():
    ENDPOINT = 'https://bbp.epfl.ch/edx-single-cell/answer'

    def __init__(self, hideToken=False):
        self.hideToken = hideToken
        if self.hideToken == True:
            display(Javascript('''
                var token = IPython ? IPython.notebook.metadata.submission_token : null;
                var rollback = false;
                if (!token) {
                    console.debug('Token absent from metadata. Rollback to manual token input');
                    rollback = true;
                }

                console.debug(`Has Token: ${token ? true : false}`);
                console.debug(`Rollback: ${rollback}`);

                IPython.notebook.kernel.execute(`TOKEN = "${token}"`);
                IPython.notebook.kernel.execute(`ROLLBACK = "${rollback}"`);
            '''))
        else:
            self.show_submission()


    def show_submission(self, ROLLBACK='true', TOKEN=''):
        output = []
        self.token = TOKEN
        if ROLLBACK == 'true': self.hideToken = False

        if not self.hideToken:
            self.key_input = widgets.Text(
                value='',
                placeholder='Paste key here',
                description='Key:',
                layout=widgets.Layout(width='99%')
            )
            output.append(self.key_input)

        self.answer_input = widgets.Textarea(
            value='',
            placeholder='Paste answer(s)',
            description='Answer:',
            layout=widgets.Layout(width='99%')
        )
        output.append(self.answer_input)

        self.button = widgets.Button(
            description='Submit results',
            button_style='info',
            icon='check'
        )
        self.button.on_click(self.submit_answer)
        self.button.add_class('centered')
        output.append(self.button)
        if self.hideToken:
            info_token = widgets.Label('(If you need to enter a key, '
                                       'go back to the course platform and get '
                                       'a submission key from the exercise page)')
            info_token.add_class('centered')
            output.append(info_token)

        self.answers_list = widgets.HTML() # to always keep on top
        output.append(self.answers_list)

        self.messages = widgets.HTML()
        output.append(self.messages)

        self.show_output(output)


    def show_output(self, output=[]):
        style = widgets.HTML('''<style>
            .custom-inputs .errors { color: #d9534f; font-size: 14px; }
            .custom-inputs .logs { margin: 10px 0 0 90px; }
            .custom-inputs .success { color: #468d89; }
            .custom-inputs .form-control { width: 80%; margin-bottom: 10px; }
            .custom-inputs .answers { font-size: 18px; margin-top: 10px; }
            .custom-inputs .centered { margin: 10px auto; }
        </style>''')
        output.append(style)

        self.inputs = widgets.VBox(
            children=output,
            layout=widgets.Layout(margin='10px 0px 10px 0px')
        )
        self.inputs.add_class('custom-inputs')

        display(self.inputs)


    def submit_answer(self, value):
        self.messages.value = ''
        data = {}

        if self.hideToken:
            key = self.token
        else:
            key = self.key_input.value
            if not key:
                return self.show_message('Key missing. Please paste your key '
                                         'here and try again', 'errors')
        data['submission_token'] = key

        answers = self.answer_input.value
        if not answers:
            return self.show_message('Answer(s) missing. Please fill the '
                                     'answer field and try again', 'errors')
        data['answer'] = answers

        self.show_answers(answers)
        self.show_message('Submitting...')

        try:
            response = requests.post(self.ENDPOINT, json=data)
        except ValueError:
            return self.show_message('Error sending the answers', 'errors', append=True)
        else:
            if response.status_code == requests.codes.ok:
                grade = response.json()['grade']
                self.show_message('Your answer was submitted successfully!','success')
                self.show_message('<p>GRADE: {:.2}</p>'.format(grade['value']), append=True)
                if 'feedback' in grade:
                    self.show_message('<p>FEEDBACK: {}</p>'.format(grade['feedback']), append=True)
                platform = response.json()['platform']
                self.show_message('<p>Your grade is also available on <a href="{0}" target="_blank">{0}</a></p>'.format(platform), append=True)
            else:
                self.show_message(response.json()['message'], 'errors')


    def show_message(self, message, type_message='', append=False):
        msg = '<div class="logs {}">{}</div>'.format(type_message, message)
        if append:
            self.messages.value += msg
        else:
            self.messages.value = msg


    def show_answers(self, answers):
        msg = '<div class="logs answers">Your answer(s): {}</div>'.format(answers)
        self.answers_list.value = msg