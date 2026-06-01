// AnakinFlightSchool — ADronePawn
// Kinematic CTBR (collective-thrust + body-rate) drone, ported bit-identically from the
// validated numpy reference (ue5_sim/scripts/drone_test.py, DRONE_DYNAMICS.md, 2026-06-01).
// Keeping the arithmetic identical to numpy preserves teacher<->student transfer validity.
//
// UE convention (validated in-engine): LEFT-HANDED, Z up, X forward, Y right. Body thrust +Z.
// Control-sign spec (THE spec — wire policy/adapter to this or flight inverts):
//   collective ↑ -> +Z (up)      pitch wy>0 -> +X (forward)
//   roll  wx>0  -> −Y (left)      yaw   wz>0 -> +heading (CCW)
//
// Units are UE-native centimetres / seconds. Internal state is double precision to match numpy.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "DronePawn.generated.h"

UCLASS()
class ANAKINFLIGHTSCHOOL_API ADronePawn : public APawn
{
	GENERATED_BODY()

public:
	ADronePawn();

	// --- Tuned dynamics constants (UE units: cm, s) ---
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Drone|Dynamics")
	double G = 981.0;            // gravity, cm/s^2

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Drone|Dynamics")
	double TWR = 3.85;           // thrust-to-weight (our calibration); hover collective = 1/TWR

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Drone|Dynamics")
	double CD = 0.3;             // linear drag, 1/s

	// Advance ONE fixed timestep. action = collective[0..1], body rates wx,wy,wz (rad/s).
	// Pure, deterministic, decoupled from wall-clock — the bridge calls this at fixed Dt.
	UFUNCTION(BlueprintCallable, Category = "Drone")
	void Step(float Collective, float Wx, float Wy, float Wz, float Dt);

	// Reset to rest at StartLocation, level orientation, zero velocity.
	UFUNCTION(BlueprintCallable, Category = "Drone")
	void ResetState(FVector StartLocation);

	// Full 10-dim state: [px,py,pz, vx,vy,vz, qw,qx,qy,qz]. (Validation / debugging.)
	UFUNCTION(BlueprintCallable, Category = "Drone")
	TArray<float> GetStateVector() const;

	// Push the current dynamics state onto the actor transform (call after Step for visuals).
	UFUNCTION(BlueprintCallable, Category = "Drone")
	void SyncVisual();

	// Visual root (a mesh can be assigned in editor/Blueprint; not required for headless training).
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Drone")
	TObjectPtr<class UStaticMeshComponent> Body;

private:
	// Double-precision dynamics state, mirroring the numpy reference exactly.
	double Px = 0, Py = 0, Pz = 0;       // position (cm)
	double Vx = 0, Vy = 0, Vz = 0;       // velocity (cm/s)
	double Qw = 1, Qx = 0, Qy = 0, Qz = 0; // orientation quaternion (w,x,y,z)
};
