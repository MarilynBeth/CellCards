createOntologyTerm = """
CREATE TABLE `t_ontology_term` (
  `c_ontology_term_id` varchar(25) NOT NULL,
  `c_name` varchar(255) DEFAULT NULL,
  `c_definition` varchar(2000) DEFAULT NULL,
  `c_source` varchar(200) DEFAULT NULL,
  `c_category` varchar(200) DEFAULT NULL,
  `c_is_user_defined` varchar(100) DEFAULT NULL,
  `c_uri` varchar(500) DEFAULT NULL,
  `c_notes` varchar(4000) DEFAULT NULL,
  `c_minimum_level` int DEFAULT NULL,
  `c_maximum_level` int DEFAULT NULL,
  `c_number_of_levels` int DEFAULT NULL,
  `c_database_reference` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`c_ontology_term_id`)
);
"""

createTsynonymTable = """CREATE TABLE `t_synonym` (
  `c_synonym_id` int NOT NULL AUTO_INCREMENT,
  `c_synonym_label` varchar(2000) NOT NULL,
  `c_ontology_term_id` varchar(25) NOT NULL,
  `c_synonym_annotation_property_label` varchar(100) DEFAULT NULL,
  `c_synonym_annotation_property_iri` varchar(25) DEFAULT NULL,
  `c_synonym_type` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`c_synonym_id`),
  KEY `synonym_onto_term_id` (`c_ontology_term_id`),
  CONSTRAINT `synonym_onto_term_id` FOREIGN KEY (`c_ontology_term_id`) REFERENCES `t_ontology_term` (`c_ontology_term_id`)
)"""

createOntologyTermRelation = """
CREATE TABLE `t_ontology_term_relation` (
  `c_relationship_id` int NOT NULL AUTO_INCREMENT,
  `c_subject_term_label` varchar(2000) DEFAULT NULL,
  `c_subject_term_id` varchar(100) DEFAULT NULL,
  `c_predicate_term_label` varchar(100) DEFAULT NULL,
  `c_predicate_term_id` varchar(100) DEFAULT NULL,
  `c_object_term_label` varchar(1000) DEFAULT NULL,
  `c_object_term_id` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`c_relationship_id`)
)"""



create_t_cells_table = """CREATE TABLE `t_cells` (
  `c_cell_id` int NOT NULL AUTO_INCREMENT,
  `c_cell_ontology_term_id` varchar(25) DEFAULT NULL,
  `c_cell_name` varchar(200) DEFAULT NULL,
  `c_related_ontology_id` varchar(30) DEFAULT NULL,
  `c_related_ontology_label` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`c_cell_id`),
  KEY `c_cell_onto_term_id` (`c_cell_ontology_term_id`),
  CONSTRAINT `c_cell_onto_term_id` FOREIGN KEY (`c_cell_ontology_term_id`) REFERENCES `t_ontology_term` (`c_ontology_term_id`)
)"""

create_t_gene_protein_table = """CREATE TABLE `t_gene_protein` (
  `c_gene_prot_id` int NOT NULL AUTO_INCREMENT,
  `c_entrez_gene_id` varchar(100) DEFAULT NULL,
  `c_cell_id` int NOT NULL,
  `c_HGNC_id` varchar(100) DEFAULT NULL,
  `c_gene_label` varchar(200) DEFAULT NULL,
  `c_OGG_id` varchar(100) DEFAULT NULL,
  `c_PR_id` varchar(200) DEFAULT NULL,
  `c_description` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`c_gene_prot_id`),
  KEY `gene_prot_onto_term_id` (`c_cell_id`),
  CONSTRAINT `gene_prot_onto_term_id` FOREIGN KEY (`c_cell_id`) REFERENCES `t_cells` (`c_cell_id`)
)"""