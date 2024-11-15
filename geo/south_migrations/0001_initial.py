# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Country'
        db.create_table(u'geo_country', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=2, db_index=True)),
            ('code3', self.gf('django.db.models.fields.CharField')(max_length=3, db_index=True)),
            ('population', self.gf('django.db.models.fields.IntegerField')()),
            ('area', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=3, null=True)),
            ('currency_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('languages', self.gf('django.db.models.fields.CharField')(max_length=250, null=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('continent', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('tld', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('capital', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'geo', ['Country'])

        # Adding M2M table for field alt_names on 'Country'
        m2m_table_name = db.shorten_name(u'geo_country_alt_names')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('country', models.ForeignKey(orm[u'geo.country'], null=False)),
            ('alternativename', models.ForeignKey(orm[u'geo.alternativename'], null=False))
        ))
        db.create_unique(m2m_table_name, ['country_id', 'alternativename_id'])

        # Adding M2M table for field neighbours on 'Country'
        m2m_table_name = db.shorten_name(u'geo_country_neighbours')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_country', models.ForeignKey(orm[u'geo.country'], null=False)),
            ('to_country', models.ForeignKey(orm[u'geo.country'], null=False))
        ))
        db.create_unique(m2m_table_name, ['from_country_id', 'to_country_id'])

        # Adding model 'Region'
        db.create_table(u'geo_region', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('name_std', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.Country'])),
        ))
        db.send_create_signal(u'geo', ['Region'])

        # Adding M2M table for field alt_names on 'Region'
        m2m_table_name = db.shorten_name(u'geo_region_alt_names')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('region', models.ForeignKey(orm[u'geo.region'], null=False)),
            ('alternativename', models.ForeignKey(orm[u'geo.alternativename'], null=False))
        ))
        db.create_unique(m2m_table_name, ['region_id', 'alternativename_id'])

        # Adding model 'Subregion'
        db.create_table(u'geo_subregion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('name_std', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('region', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.Region'])),
        ))
        db.send_create_signal(u'geo', ['Subregion'])

        # Adding M2M table for field alt_names on 'Subregion'
        m2m_table_name = db.shorten_name(u'geo_subregion_alt_names')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('subregion', models.ForeignKey(orm[u'geo.subregion'], null=False)),
            ('alternativename', models.ForeignKey(orm[u'geo.alternativename'], null=False))
        ))
        db.create_unique(m2m_table_name, ['subregion_id', 'alternativename_id'])

        # Adding model 'City'
        db.create_table(u'geo_city', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('name_std', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('location', self.gf('django.contrib.gis.db.models.fields.PointField')()),
            ('population', self.gf('django.db.models.fields.IntegerField')()),
            ('region', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.Region'], null=True, blank=True)),
            ('subregion', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.Subregion'], null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.Country'])),
            ('elevation', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('kind', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('timezone', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal(u'geo', ['City'])

        # Adding M2M table for field alt_names on 'City'
        m2m_table_name = db.shorten_name(u'geo_city_alt_names')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('city', models.ForeignKey(orm[u'geo.city'], null=False)),
            ('alternativename', models.ForeignKey(orm[u'geo.alternativename'], null=False))
        ))
        db.create_unique(m2m_table_name, ['city_id', 'alternativename_id'])

        # Adding model 'District'
        db.create_table(u'geo_district', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('name_std', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('location', self.gf('django.contrib.gis.db.models.fields.PointField')()),
            ('population', self.gf('django.db.models.fields.IntegerField')()),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.City'])),
        ))
        db.send_create_signal(u'geo', ['District'])

        # Adding M2M table for field alt_names on 'District'
        m2m_table_name = db.shorten_name(u'geo_district_alt_names')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('district', models.ForeignKey(orm[u'geo.district'], null=False)),
            ('alternativename', models.ForeignKey(orm[u'geo.alternativename'], null=False))
        ))
        db.create_unique(m2m_table_name, ['district_id', 'alternativename_id'])

        # Adding model 'AlternativeName'
        db.create_table(u'geo_alternativename', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('is_preferred', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_short', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_colloquial', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'geo', ['AlternativeName'])

        # Adding model 'PostalCode'
        db.create_table(u'geo_postalcode', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('location', self.gf('django.contrib.gis.db.models.fields.PointField')()),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(related_name='postal_codes', to=orm['geo.Country'])),
            ('region_name', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('subregion_name', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('district_name', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
        ))
        db.send_create_signal(u'geo', ['PostalCode'])

        # Adding M2M table for field alt_names on 'PostalCode'
        m2m_table_name = db.shorten_name(u'geo_postalcode_alt_names')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('postalcode', models.ForeignKey(orm[u'geo.postalcode'], null=False)),
            ('alternativename', models.ForeignKey(orm[u'geo.alternativename'], null=False))
        ))
        db.create_unique(m2m_table_name, ['postalcode_id', 'alternativename_id'])

    def backwards(self, orm):
        # Deleting model 'Country'
        db.delete_table(u'geo_country')

        # Removing M2M table for field alt_names on 'Country'
        db.delete_table(db.shorten_name(u'geo_country_alt_names'))

        # Removing M2M table for field neighbours on 'Country'
        db.delete_table(db.shorten_name(u'geo_country_neighbours'))

        # Deleting model 'Region'
        db.delete_table(u'geo_region')

        # Removing M2M table for field alt_names on 'Region'
        db.delete_table(db.shorten_name(u'geo_region_alt_names'))

        # Deleting model 'Subregion'
        db.delete_table(u'geo_subregion')

        # Removing M2M table for field alt_names on 'Subregion'
        db.delete_table(db.shorten_name(u'geo_subregion_alt_names'))

        # Deleting model 'City'
        db.delete_table(u'geo_city')

        # Removing M2M table for field alt_names on 'City'
        db.delete_table(db.shorten_name(u'geo_city_alt_names'))

        # Deleting model 'District'
        db.delete_table(u'geo_district')

        # Removing M2M table for field alt_names on 'District'
        db.delete_table(db.shorten_name(u'geo_district_alt_names'))

        # Deleting model 'AlternativeName'
        db.delete_table(u'geo_alternativename')

        # Deleting model 'PostalCode'
        db.delete_table(u'geo_postalcode')

        # Removing M2M table for field alt_names on 'PostalCode'
        db.delete_table(db.shorten_name(u'geo_postalcode_alt_names'))

    models = {
        u'geo.alternativename': {
            'Meta': {'object_name': 'AlternativeName'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_colloquial': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_preferred': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_short': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'geo.city': {
            'Meta': {'object_name': 'City'},
            'alt_names': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['geo.AlternativeName']", 'symmetrical': 'False'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['geo.Country']"}),
            'elevation': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'name_std': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'population': ('django.db.models.fields.IntegerField', [], {}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['geo.Region']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'subregion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['geo.Subregion']", 'null': 'True', 'blank': 'True'}),
            'timezone': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        u'geo.country': {
            'Meta': {'ordering': "['name']", 'object_name': 'Country'},
            'alt_names': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['geo.AlternativeName']", 'symmetrical': 'False'}),
            'area': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'capital': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2', 'db_index': 'True'}),
            'code3': ('django.db.models.fields.CharField', [], {'max_length': '3', 'db_index': 'True'}),
            'continent': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True'}),
            'currency_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languages': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'neighbours': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'neighbours_rel_+'", 'to': u"orm['geo.Country']"}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'population': ('django.db.models.fields.IntegerField', [], {}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'tld': ('django.db.models.fields.CharField', [], {'max_length': '5'})
        },
        u'geo.district': {
            'Meta': {'object_name': 'District'},
            'alt_names': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['geo.AlternativeName']", 'symmetrical': 'False'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['geo.City']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'name_std': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'population': ('django.db.models.fields.IntegerField', [], {}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'geo.postalcode': {
            'Meta': {'object_name': 'PostalCode'},
            'alt_names': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['geo.AlternativeName']", 'symmetrical': 'False'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'postal_codes'", 'to': u"orm['geo.Country']"}),
            'district_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'region_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'subregion_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'})
        },
        u'geo.region': {
            'Meta': {'object_name': 'Region'},
            'alt_names': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['geo.AlternativeName']", 'symmetrical': 'False'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['geo.Country']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'name_std': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'geo.subregion': {
            'Meta': {'object_name': 'Subregion'},
            'alt_names': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['geo.AlternativeName']", 'symmetrical': 'False'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'name_std': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['geo.Region']"}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['geo']
