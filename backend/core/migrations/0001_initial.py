from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('diagnosis', models.CharField(max_length=200)),
                ('discipline', models.CharField(max_length=120)),
                ('doctor', models.CharField(blank=True, default='', max_length=120)),
                ('admitted', models.CharField(default='Yes', max_length=8)),
                ('admission_date', models.DateField(blank=True, null=True)),
                ('day', models.IntegerField(default=0)),
                ('sticker', models.CharField(blank=True, default='', max_length=120)),
                ('remarks', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='patients_created', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Audit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('at', models.DateTimeField(auto_now_add=True)),
                ('actor', models.CharField(max_length=64)),
                ('role', models.CharField(max_length=24)),
                ('action', models.CharField(max_length=64)),
                ('details', models.JSONField(default=dict)),
            ],
        ),
    ]
