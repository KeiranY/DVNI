# Add teacher profile
useradd -m "teacher"
# Set password
echo "teacher:teacher" | chpasswd
# Force password change on login
chage -d 0 teacher
# Execute DVNG start.py on login
echo "sudo PYTHONPATH=/vagrant /usr/bin/python /vagrant/start.py teacher" >> /home/teacher/.profile
# Then logout
echo "read -p 'Press enter to continue'" >> /home/teacher/.profile
echo "exit 0" >> /home/teacher/.profile
# Allow user of sudo, required for containernet
echo "teacher ALL=NOPASSWD: ALL" >> /etc/sudoers

# Add student profile in a similar manner
useradd -m "student"
echo "student:student" | chpasswd
echo "sudo PYTHONPATH=/vagrant /usr/bin/python /vagrant/start.py student" >> /home/student/.profile
echo "read -p 'Press enter to continue'" >> /home/student/.profile
echo "exit 0" >> /home/student/.profile
echo "student ALL=NOPASSWD: ALL" >> /etc/sudoers

# Configure ssh to allow password logins for these accounts
echo "Match User teacher,student" >> /etc/ssh/sshd_config
echo "    PasswordAuthentication yes" >> /etc/ssh/sshd_config
service ssh reload

# Update pip
pip install -U pip
# Install required python modules
pip2 install -U networkx python-docx matplotlib pyftpdlib typing sphinx sphinx_rtd_theme