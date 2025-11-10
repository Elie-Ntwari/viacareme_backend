# Generated manually for adding medecins ManyToMany field to Patiente model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medical_module', '0001_initial'),
        ('patiente__module', '0003_patiente_creer_a_hopital'),
    ]

    operations = [
        migrations.CreateModel(
            name='PatienteMedecins',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('patiente', models.ForeignKey(on_delete=models.CASCADE, to='patiente__module.patiente')),
                ('medecin', models.ForeignKey(on_delete=models.CASCADE, to='medical_module.medecin')),
            ],
            options={
                'db_table': 'patiente_medecins',
                'unique_together': {('patiente', 'medecin')},
            },
        ),
        migrations.AddField(
            model_name='patiente',
            name='medecins',
            field=models.ManyToManyField(blank=True, related_name='patientes_assignees', through='patiente__module.PatienteMedecins', to='medical_module.medecin'),
        ),
    ]