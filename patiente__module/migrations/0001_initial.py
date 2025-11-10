# Generated manually

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth_module', '0001_initial'),
        ('hospital_module', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Patiente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_naissance', models.DateField(blank=True, null=True)),
                ('adresse', models.CharField(blank=True, max_length=255, null=True)),
                ('ville', models.CharField(blank=True, max_length=100, null=True)),
                ('province', models.CharField(blank=True, max_length=100, null=True)),
                ('numero_identification', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('date_inscription', models.DateTimeField(default=django.utils.timezone.now)),
                ('has_carte', models.BooleanField(default=False)),
                ('creer_a_hopital', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='patientes_creees', to='hospital_module.hopital')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profil_patiente', to='auth_module.user')),
            ],
            options={
                'db_table': 'patiente',
            },
        ),
    ]