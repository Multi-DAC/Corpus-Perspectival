// AnakinFlightSchool — ADronePawn implementation. See DronePawn.h for the contract + sign spec.

#include "DronePawn.h"
#include "Components/StaticMeshComponent.h"

namespace
{
	// Hamilton quaternion product, (w,x,y,z) convention — identical to numpy reference quat_mul.
	FORCEINLINE void QuatMul(
		double aw, double ax, double ay, double az,
		double bw, double bx, double by, double bz,
		double& ow, double& ox, double& oy, double& oz)
	{
		ow = aw * bw - ax * bx - ay * by - az * bz;
		ox = aw * bx + ax * bw + ay * bz - az * by;
		oy = aw * by - ax * bz + ay * bw + az * bx;
		oz = aw * bz + ax * by - ay * bx + az * bw;
	}

	// Rotate vector v by quaternion q (w,x,y,z) — identical to numpy reference rot_vec.
	FORCEINLINE void RotVec(
		double w, double x, double y, double z,
		double vx, double vy, double vz,
		double& rx, double& ry, double& rz)
	{
		const double tx = 2.0 * (y * vz - z * vy);
		const double ty = 2.0 * (z * vx - x * vz);
		const double tz = 2.0 * (x * vy - y * vx);
		rx = vx + w * tx + (y * tz - z * ty);
		ry = vy + w * ty + (z * tx - x * tz);
		rz = vz + w * tz + (x * ty - y * tx);
	}
}

ADronePawn::ADronePawn()
{
	PrimaryActorTick.bCanEverTick = false; // dynamics are driven explicitly via Step(), not the tick

	Body = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Body"));
	RootComponent = Body;
	Body->SetMobility(EComponentMobility::Movable);
	Body->SetCollisionEnabled(ECollisionEnabled::QueryOnly); // bridge handles physics; collision = gate/decor queries
}

void ADronePawn::ResetState(FVector StartLocation)
{
	Px = StartLocation.X; Py = StartLocation.Y; Pz = StartLocation.Z;
	Vx = Vy = Vz = 0.0;
	Qw = 1.0; Qx = Qy = Qz = 0.0; // level
	SyncVisual();
}

void ADronePawn::Step(float Collective, float Wx, float Wy, float Wz, float Dt)
{
	const double TMAX = TWR * G; // max thrust accel (cm/s^2); hover collective = 1/TWR
	const double dt = Dt;

	// --- integrate orientation by body rates (rate-controlled / ACRO) ---
	const double half = dt * 0.5;
	double nw, nx, ny, nz;
	QuatMul(Qw, Qx, Qy, Qz,
	        1.0, Wx * half, Wy * half, Wz * half,
	        nw, nx, ny, nz);
	double n = FMath::Sqrt(nw * nw + nx * nx + ny * ny + nz * nz);
	if (n == 0.0) { n = 1.0; }
	Qw = nw / n; Qx = nx / n; Qy = ny / n; Qz = nz / n;

	// --- thrust along body +Z, rotated to world ---
	double twx, twy, twz;
	RotVec(Qw, Qx, Qy, Qz, 0.0, 0.0, Collective * TMAX, twx, twy, twz);

	const double ax = twx - CD * Vx;
	const double ay = twy - CD * Vy;
	const double az = twz - G - CD * Vz;

	// --- semi-implicit Euler ---
	Vx += ax * dt; Vy += ay * dt; Vz += az * dt;
	Px += Vx * dt; Py += Vy * dt; Pz += Vz * dt;
}

TArray<float> ADronePawn::GetStateVector() const
{
	return TArray<float>{
		(float)Px, (float)Py, (float)Pz,
		(float)Vx, (float)Vy, (float)Vz,
		(float)Qw, (float)Qx, (float)Qy, (float)Qz
	};
}

void ADronePawn::SyncVisual()
{
	// UE FQuat is (X,Y,Z,W); our state is (w,x,y,z).
	const FQuat Rot((float)Qx, (float)Qy, (float)Qz, (float)Qw);
	SetActorLocationAndRotation(FVector(Px, Py, Pz), Rot, /*bSweep=*/false, nullptr, ETeleportType::TeleportPhysics);
}
