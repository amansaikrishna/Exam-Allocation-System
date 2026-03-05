# Make sure you're in backend/ with env activated
cd ~/Desktop/Hackathon/backend
source env/bin/activate

python3 manage.py makemigrations allocation
python3 manage.py migrate

# Create the first ADMIN user
python3 manage.py shell -c "
from allocation.models import User
if not User.objects.filter(username='admin').exists():
    u = User.objects.create_superuser('admin', 'admin@exam.com', 'admin123')
    u.role = 'ADMIN'
    u.save()
    print('Admin created: admin / admin123')
else:
    print('Admin already exists')
"

# Start server
python3 manage.py runserver
