from typing import Literal, NotRequired, TypedDict

SternType = Literal[
    "normal_shaped_sections",
    "v_shaped_sections",
    "u_shaped_sections_with_hogner_stern",
    "pram_with_gondola",
]
PropulsionType = Literal[
    "single_screw_conventional_stern",
    "single_screw_open_flow_stern",
    "twin_screw",
]
WaterType = Literal["salt_water_15_c", "fresh_water_15_c", "custom"]
ModelingMode = Literal["user", "estimated"]
AppendageMode = Literal["percent_bare_hull_resistance", "equivalent_area_form_factor"]


class Project(TypedDict):
    name: str
    run_id: str


class SpeedSweep(TypedDict):
    initial_speed_knots: float
    speed_increment_knots: float
    status: NotRequired[str]


class Hull(TypedDict):
    lwl_m: float
    beam_lwl_m: float
    draft_forward_m: float
    draft_aft_m: float
    block_coefficient: float
    midship_coefficient: float
    waterplane_coefficient: float
    lcb_percent_lwl_from_midships_forward_positive: float


class Features(TypedDict):
    bulb_area_station_0_m2: float
    bulb_vertical_center_m: float
    transom_immersed_area_zero_speed_m2: float
    stern_type: SternType


class Propulsion(TypedDict):
    type: PropulsionType
    propeller_diameter_m: float
    expanded_area_ratio: float
    pitch_diameter_ratio: NotRequired[float | None]


class Appendages(TypedDict):
    mode: AppendageMode
    percent_bare_hull_resistance: NotRequired[float]
    equivalent_wetted_area_form_factor_m2: NotRequired[float | None]


class Modeling(TypedDict):
    air_drag: bool
    depth_at_bow_m: float
    deckhouse_cargo_frontal_area_m2: float
    wetted_surface_mode: ModelingMode
    wetted_surface_m2: float
    half_angle_entrance_mode: ModelingMode
    half_angle_entrance_degrees: float


class Water(TypedDict):
    type: WaterType
    density_kg_m3: float
    kinematic_viscosity_m2_s: float


class Margin(TypedDict):
    design_margin_percent: float


class Case(TypedDict):
    project: Project
    speed_sweep: SpeedSweep
    hull: Hull
    features: Features
    propulsion: Propulsion
    appendages: Appendages
    modeling: Modeling
    water: Water
    margin: Margin
    schema: NotRequired[str]
    version: NotRequired[int]
    source: NotRequired[dict[str, object]]
    legacy_labels: NotRequired[dict[str, str]]


class ApplicabilityCheck(TypedDict):
    name: str
    label: str
    value: float
    lower: float
    upper: float
    ok: bool


class EngineeringReview(TypedDict):
    statuses: list[str]
    note: str
    warnings: NotRequired[list[str]]


class SpeedRow(TypedDict, total=False):
    speed_knots: float
    speed_mps: float
    froude_number: float
    speed_length_ratio: float
    reynolds_number: float
    friction_coefficient: float
    residual_resistance_coefficient: float
    correlation_allowance_coefficient: float
    appendage_mode: AppendageMode
    appendage_equivalent_wetted_area_form_factor_m2: float | None
    frictional_resistance_n: float
    rf_form_resistance_n: float
    appendage_resistance_n: float
    wave_resistance_n: float
    bulb_resistance_n: float
    transom_resistance_n: float
    correlation_allowance_resistance_n: float
    air_resistance_n: float
    implemented_resistance_subtotal_n: float
    design_margin_resistance_n: float
    total_resistance_n: float
    effective_power_kw: float
    wake_fraction: float
    thrust_deduction: float
    required_thrust_n: float
    hull_efficiency: float
    relative_rotative_efficiency: float
    resistance_status: str


class Derived(TypedDict):
    mean_draft_m: float
    prismatic_coefficient: float
    lcb_m_from_fp: float
    lcb_percent_lwl_from_fp: float
    beam_draft_ratio: float
    draft_beam_ratio: float
    lwl_beam_ratio: float
    beam_lwl_ratio: float
    midship_area_m2: float
    waterplane_area_m2: float
    displacement_volume_m3: float
    length_displacement_ratio: float
    displacement_mass_tonnes: float


class ActiveModeling(TypedDict):
    wetted_surface_mode: ModelingMode
    wetted_surface_m2: float
    half_angle_entrance_mode: ModelingMode
    half_angle_entrance_degrees: float


class Result(TypedDict):
    project: Project
    derived: Derived
    modeling: ActiveModeling
    engineering_review: EngineeringReview
    applicability: list[ApplicabilityCheck]
    speeds: list[SpeedRow]


class LegacyInOptions(TypedDict, total=False):
    first_record_order: Literal["depth_before_drafts", "drafts_before_depth"]
    propeller_record_order: Literal["wetted_half_dp", "dp_wetted_half"]
    stern_correction: float
    pitch_diameter_ratio: float
    water_type_code: int
    propulsion_type_code: int
    appendage_primary_value: float
    appendage_model_total: float
