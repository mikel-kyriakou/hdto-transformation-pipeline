from rdflib import Namespace, Graph, URIRef, Literal
from rdflib.namespace import RDF, XSD

from app.models.models import HeritageObjectData

CIDOC = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
RHDTO = Namespace("https://vast-lab.org/rhdto/")
#TODO change this
OUR_NAMESPACE = Namespace("http://aueb.gr/rhdto-transofmration-pipeline/")


class Mapper:

    def __init__(self, cidoc_crm: Namespace = CIDOC, rhdto: Namespace = RHDTO) -> None:
        self.cidoc_crm = cidoc_crm
        self.rhdto = rhdto
        self.our_namespace = OUR_NAMESPACE

    def map(self, heritage_objects: list[HeritageObjectData]) -> Graph:
        self.instance_registry: dict[tuple[URIRef, str], URIRef] = {}

        graph = Graph()
        graph.bind("crm", self.cidoc_crm)
        graph.bind("rhdto", self.rhdto)

        for index, obj in enumerate(heritage_objects):
            object_instance = self._create_instance(
                graph=graph,
                instance_id=f"tangible-entity-{index}",
                class_type=self.rhdto.HC3_Tangible_Entity
            )

            self._add_identifier(graph, object_instance, index, obj.id)

            self._add_title(graph, object_instance, index, obj.title)

            self._add_type(graph, object_instance, index, obj.object_type)

            self._add_material(graph, object_instance, index, obj.material)

            # self._add_collections()

            self._add_representation(graph, object_instance, index, obj.representation)
            # self._add_depiction
            # self._add_part_of

            self._add_language(graph, object_instance, index, obj.language)
            self._add_reference(graph, object_instance, index, obj.reference)

            self._add_creation_date(graph, object_instance, index, obj.creation_date)
            self._add_creation_date(graph, object_instance, index, obj.destruction_date)

            self._add_place_of_creation(graph, object_instance, index, obj.place_of_creation)
            self._add_place_of_destruction(graph, object_instance, index, obj.place_of_destruction)

            # self._add_creators()

            self._add_digital_representation(graph, object_instance, index, obj.digital_representation)

        return graph

    # =========================================================
    # ADD / MAPPING METHODS
    # =========================================================

    def _add_identifier(self, graph: Graph, object_instance: URIRef, instance_index: int, value: str | None) -> None:

        if value is None:
            return

        identifier_instance = self._create_instance_with_literal(
            graph=graph,
            instance_id=f"identifier-{instance_index}",
            class_type=self.cidoc_crm.E42_Identifier,
            literal_value=value
        )

        graph.add((object_instance, self.cidoc_crm.P48_has_preferred_identifier, identifier_instance))

    def _add_title(self, graph: Graph, object_instance: URIRef, instance_index: int, value: str | None) -> None:

        if value is None:
            return

        title_instance = self._create_instance_with_literal(
            graph=graph,
            instance_id=f"title-{instance_index}",
            class_type=self.cidoc_crm.E35_Title,
            literal_value=value
        )

        graph.add((object_instance, self.cidoc_crm.P102_has_title, title_instance))

    def _add_type(self, graph: Graph, object_instance: URIRef, instance_index: int, value: str | None) -> None:

        if value is None:
            return

        type_instance = self._get_or_create_instance_with_literal(
            graph=graph,
            instance_id=f"type-{instance_index}",
            class_type=self.cidoc_crm.E55_Type,
            literal_value=value
        )

        graph.add((object_instance, self.cidoc_crm.P2_has_type, type_instance))

    def _add_material(self, graph: Graph, object_instance: URIRef, instance_index: int, value: str | None) -> None:

        if value is None:
            return

        material_instance = self._get_or_create_instance_with_literal(
            graph=graph,
            instance_id=f"material-{instance_index}",
            class_type=self.cidoc_crm.E57_Material,
            literal_value=value
        )

        graph.add((object_instance, self.cidoc_crm.P45_consists_of, material_instance))

    def _add_representation(self, graph: Graph, object_instance: URIRef, instance_index: int, value: str | None) -> None:

        if value is None:
            return

        representation_instance = self._create_instance_with_literal(
            graph=graph,
            instance_id=f"representation-{instance_index}",
            class_type=self.cidoc_crm.E36_Visual_Item,
            literal_value=value,
        )

        graph.add((object_instance, self.cidoc_crm.P138_has_representation, representation_instance))

    def _add_language(self, graph: Graph, object_instance: URIRef, instance_index: int, value: str | None) -> None:

        if value is None:
            return

        linguistic_obj_instance = self._get_or_create_instance(
            graph=graph,
            instance_id=f"linguistic-object-{instance_index}",
            class_type=self.cidoc_crm.E33_Linguistic_Object,
        )

        language_instance = self._get_or_create_instance_with_literal(
            graph=graph,
            instance_id=f"language-{instance_index}",
            class_type=self.cidoc_crm.E56_Language,
            literal_value=value,
        )

        graph.add((object_instance, self.cidoc_crm.P128_carries, linguistic_obj_instance))
        graph.add((linguistic_obj_instance, self.cidoc_crm.P72_has_language, language_instance))

    def _add_reference(self, graph: Graph, object_instance: URIRef, instance_index: int, value: str | None) -> None:

        if value is None:
            return

        linguistic_obj_instance = self._get_or_create_instance(
            graph=graph,
            instance_id=f"linguistic-object-{instance_index}",
            class_type=self.cidoc_crm.E33_Linguistic_Object,
        )

        thing_instance = self._get_or_create_instance_with_literal(
            graph=graph,
            instance_id=f"reference-thing-{instance_index}",
            class_type=self.cidoc_crm.E70_Thing,
            literal_value=value,
        )

        graph.add((object_instance, self.cidoc_crm.P128_carries, linguistic_obj_instance))
        graph.add((linguistic_obj_instance, self.cidoc_crm.P67_refers_to, thing_instance))

    def _add_creation_date(self, graph: Graph, object_instance: URIRef, instance_index: int, value: str | None) -> None:

        if value is None:
            return

        boe_instance = self._get_or_create_instance(
            graph=graph,
            instance_id=f"beginning-of-existence-{instance_index}",
            class_type=self.cidoc_crm.E63_Beginning_of_Existence
        )

        time_span_instance = self._get_or_create_instance_with_literal(
            graph=graph,
            instance_id=f"time-span-{instance_index}",
            class_type=self.cidoc_crm["E52_Time-Span"],
            literal_value=value,
            property=self.cidoc_crm.P170i_time_is_defined_by
        )

        graph.add((boe_instance, self.cidoc_crm.P92_brought_into_existence, object_instance))
        graph.add((boe_instance, self.cidoc_crm["P4_has_time-span"], time_span_instance))

    def _add_destruction_date(self, graph: Graph, object_instance: URIRef, instance_index: int, value: str | None) -> None:

        if value is None:
            return

        eoe_instance = self._get_or_create_instance(
            graph=graph,
            instance_id=f"end-of-existence-{instance_index}",
            class_type=self.cidoc_crm.E64_End_of_Existence
        )

        time_span_instance = self._get_or_create_instance_with_literal(
            graph=graph,
            instance_id=f"time-span-{instance_index}",
            class_type=self.cidoc_crm["E52_Time-Span"],
            literal_value=value,
            property=self.cidoc_crm.P170i_time_is_defined_by
        )

        graph.add((eoe_instance, self.cidoc_crm.P93_took_out_of_existence, object_instance))
        graph.add((eoe_instance, self.cidoc_crm["P4_has_time-span"], time_span_instance))

    def _add_place_of_creation(self, graph: Graph, object_instance: URIRef, instance_index: int, value: str | None) -> None:

        if value is None:
            return

        boe_instance = self._get_or_create_instance(
            graph=graph,
            instance_id=f"beginning-of-existence-{instance_index}",
            class_type=self.cidoc_crm.E63_Beginning_of_Existence
        )

        place_instance = self._get_or_create_instance_with_literal(
            graph=graph,
            instance_id=f"place-instance-{instance_index}",
            class_type=self.cidoc_crm.E53_Place,
            literal_value=value
        )

        graph.add((boe_instance, self.cidoc_crm.P92_brought_into_existence, object_instance))
        graph.add((boe_instance, self.cidoc_crm.P7_took_place_at , place_instance))

    def _add_place_of_destruction(self, graph: Graph, object_instance: URIRef, instance_index: int, value: str | None) -> None:

        if value is None:
            return

        eoe_instance = self._get_or_create_instance(
            graph=graph,
            instance_id=f"end-of-existence-{instance_index}",
            class_type=self.cidoc_crm.E64_End_of_Existence
        )

        place_instance = self._get_or_create_instance_with_literal(
            graph=graph,
            instance_id=f"place-instance-{instance_index}",
            class_type=self.cidoc_crm.E53_Place,
            literal_value=value
        )

        graph.add((eoe_instance, self.cidoc_crm.P93_took_out_of_existence, object_instance))
        graph.add((eoe_instance, self.cidoc_crm.P7_took_place_at , place_instance))

    # def _add_creators(self, graph: Graph, object_instance: URIRef, instance_index: int, value: str | None) -> None:

    #     if value is None:
    #         return

    #     boe_instance = self._get_or_create_instance(
    #         graph=graph,
    #         instance_id=f"beginning-of-existence-{instance_index}",
    #         class_type=self.cidoc_crm.E63_Beginning_of_Existence
    #     )

    #     actor_instance = self

    def _add_digital_representation(self, graph: Graph, object_instance: URIRef, instance_index: int, value: str | None) -> None:

        if value is None:
            return

        digital_repr_instance = self._create_instance_with_literal(
            graph=graph,
            instance_id=f"digital-representation-{instance_index}",
            class_type=self.rhdto.HC5_Digital_Representation,
            literal_value=value,
            property=self.rhdto.HP24_has_access_point
        )

        graph.add((object_instance, self.rhdto.HP22_has_digital_representation, digital_repr_instance))

    # ---------------------------------------------------------
    # Generic RDF creation methods
    # ---------------------------------------------------------

    def _create_instance(self, graph: Graph, instance_id: str, class_type: URIRef) -> URIRef:
        instance = self.our_namespace[instance_id]

        graph.add((instance, RDF.type, class_type))

        return instance

    def _get_or_create_instance(self, graph: Graph, instance_id: str, class_type: URIRef) -> URIRef:
        instance_key = (class_type, instance_id)
        if instance_key in self.instance_registry:
            return self.instance_registry[instance_key]

        instance = self._create_instance(graph, instance_id, class_type)

        self.instance_registry[instance_key] = instance

        return instance

    def _create_instance_with_literal(self, graph: Graph, instance_id: str, class_type: URIRef, literal_value: str, datatype: XSD | None = None, property: URIRef = None) -> URIRef:
        instance = self._create_instance(graph, instance_id, class_type)

        if property is None:
            property = self.cidoc_crm.P190_has_symbolic_content

        graph.add((instance, property, Literal(literal_value, datatype=datatype or XSD.string)))

        return instance

    def _get_or_create_instance_with_literal(self, graph: Graph, instance_id: str, class_type: URIRef, literal_value: str, literal_datatype: XSD | None = None, property: URIRef = None) -> URIRef:
        instance_key = (class_type, literal_value)
        if instance_key in self.instance_registry:
            return self.instance_registry[instance_key]

        instance = self._create_instance_with_literal(graph, instance_id, class_type, literal_value, literal_datatype, property)

        self.instance_registry[instance_key] = instance

        return instance

def get_mapper() -> Mapper:
    return Mapper()

if __name__ == "__main__":

    mapper = Mapper()

    graph = mapper.map(heritage_objects=[
        # HeritageObjectData(
        #     id="1",
        #     title="Test Object",
        #     object_type="Test Type",
        #     material="Test Material"
        # ),
        HeritageObjectData(
            id="2",
            title="Test Object 2",
            object_type="Test Type 2",
            material="Test Material 2",
            representation="https://aueb.gr/repr-url",
            language="English",
            reference="Thor",
            creation_date="1900",
            destruction_date="2000",
            place_of_creation="Athens",
            place_of_destruction="Athens",
            digital_representation="https://dig-rep.aueb.gr"
    )])

    print(graph.serialize(format="turtle"))
