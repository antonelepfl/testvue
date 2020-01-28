from IPython import display

display.display(display.Javascript('''
   var metadata = JSON.stringify(IPython.notebook.metadata);
   var code = "import json; sys.modules['userid'].metadata = json.loads(\'\'\'" + metadata + "\'\'\')";
   IPython.notebook.kernel.execute(code);
'''))

#ll
