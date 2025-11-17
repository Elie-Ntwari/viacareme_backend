# Generated manually for ClotureGrossesse model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('grossesse_module', '0003_alter_grossesse_unique_together'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClotureGrossesse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_accouchement', models.DateField()),
                ('nombre_enfants', models.IntegerField(default=1)),
                ('genre_enfant', models.CharField(blank=True, choices=[('MASCULIN', 'Masculin'), ('FEMININ', 'Féminin'), ('INDETERMINE', 'Indéterminé')], max_length=20, null=True)),
                ('poids_naissance', models.DecimalField(blank=True, decimal_places=2, help_text='Poids en kg', max_digits=4, null=True)),
                ('taille_naissance', models.IntegerField(blank=True, help_text='Taille en cm', null=True)),
                ('type_accouchement', models.CharField(choices=[('VAGINAL', 'Accouchement vaginal'), ('CESARIENNE', 'Césarienne'), ('FORCEPS', 'Forceps'), ('VENTOUSE', 'Ventouse')], max_length=20)),
                ('issue_grossesse', models.CharField(choices=[('VIVANT', 'Enfant vivant'), ('MORT_NE', 'Mort-né'), ('FAUSSE_COUCHE', 'Fausse couche'), ('INTERRUPTION', 'Interruption médicale')], max_length=20)),
                ('complications', models.TextField(blank=True, null=True)),
                ('observations', models.TextField(blank=True, null=True)),
                ('duree_travail', models.DurationField(blank=True, help_text='Durée du travail', null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('grossesse', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='cloture', to='grossesse_module.grossesse')),
            ],
        ),
        migrations.AlterField(
            model_name='auditaction',
            name='action_type',
            field=models.CharField(choices=[('CREATE_GROSSESSE', 'Création grossesse'), ('UPDATE_GROSSESSE', 'Modification grossesse'), ('CLOTURE_GROSSESSE', 'Clôture grossesse'), ('CREATE_DOSSIER_OBS', 'Création dossier obstétrical'), ('UPDATE_DOSSIER_OBS', 'Modification dossier obstétrical'), ('ACCESS_DOSSIER', 'Accès dossier obstétrical')], max_length=50),
        ),
    ]