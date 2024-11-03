# Generated by Django 5.1.2 on 2024-10-27 04:37

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CardDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('PAN', 'PAN Card'), ('Aadhaar', 'Aadhaar Card')], max_length=10)),
                ('name', models.CharField(max_length=100)),
                ('father_name', models.CharField(blank=True, max_length=100, null=True)),
                ('card_number', models.CharField(max_length=50)),
                ('dob', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, max_length=10, null=True)),
                ('aadhar_number', models.CharField(blank=True, max_length=12, null=True)),
            ],
        ),
    ]
