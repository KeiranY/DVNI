from distutils.core import setup

if __name__ == "__main__":
    setup(name='DVNG',
          version='1.0',
          description='Damn Vulnerable Network Generator',
          author='Keiran Young',
          author_email='kcyoung1997@hotmail.co.uk', requires=['docx', 'sphinx', 'docker', 'mininet', 'networkx']
          )
