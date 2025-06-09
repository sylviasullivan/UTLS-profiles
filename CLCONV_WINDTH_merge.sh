#!/bin/bash

sim='0V1M0A0R0O'
bd='/xdisk/sylvia/'

## select the limited area domain around Flight 7 track
for i in $(seq 10 25); do cdo sellonlatbox,80,90,20,30 $bd$sim'/CLCONV_3D_flight/CLCONV_3D_flight_icon_tropic_00'$i'.nc' $bd$sim'/CLCONV_3D_flight/CLCONV_3D_flight_lam_icon_tropic_00'$i'.nc'; done
for i in $(seq 1 9); do cdo sellonlatbox,80,90,20,30 $bd$sim'/WINDTH_3D_flight/WINDTH_3D_flight_icon_tropic_000'$i'.nc' $bd$sim'/WINDTH_3D_flight/WINDTH_3D_flight_lam_icon_tropic_00'$i'.nc'; done

## merge the thermodynamic (WINDTH_3D) and cloud/convective (CLCONV_3D) fields
for i in $(seq 10 25); do cdo merge $bd$sim'/CLCONV_3D_flight/CLCONV_3D_flight_lam_icon_tropic_00'$i'.nc' $bd$sim'/WINDTH_3D_flight/WINDTH_3D_flight_lam_icon_tropic_00'$i'.nc' $bd$sim'/flight_tracks/ICON_flight_tropic_00'$i'.nc'; done
for i in $(seq 1 9); do cdo merge $bd$sim'/CLCONV_3D_flight/CLCONV_3D_flight_lam_icon_tropic_000'$i'.nc' $bd$sim'/WINDTH_3D_flight/WINDTH_3D_flight_lam_icon_tropic_000'$i'.nc' $bd$sim'/flight_tracks/ICON_flight_tropic_000'$i'.nc'; done


