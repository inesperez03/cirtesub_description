# cirtesub_description

Paquete de descripcion ROS 2 (Humble) para el robot CIRTESUB.

## Contenido

- `urdf/cirtesub.urdf`: modelo del robot
- `meshes/cirtesubdae.dae`: malla del casco

## Build

```bash
colcon build --packages-select cirtesub_description
source install/setup.bash
```

## Uso

```bash
ros2 pkg prefix cirtesub_description
```
