# MSDC2026 .NET skeleton

This branch adds a C#/.NET skeleton for native Windows desktop applications (WinForms) that share a common EF Core DbContext.

Apps created (skeletons):
- Admin
- Pharmacy
- Admission
- Reception
- Lab
- Statistics
- MedicalInventory
- Clinic

Usage
1. Set the DATABASE_CONNECTION environment variable on the target machine (SQL Server connection string), e.g.:
   setx DATABASE_CONNECTION "Server=yourserver;Database=msdc;User Id=appuser;Password=secret;TrustServerCertificate=True;"

2. Build locally (requires .NET 8 SDK):
   dotnet publish Apps/Admin/Admin.csproj -c Release -r win-x64 /p:PublishSingleFile=true /p:SelfContained=true -o publish/admin

3. CI builds are configured in `.github/workflows/build-dotnet-executables.yml` and will publish single-file self-contained exes and upload them as workflow artifacts.

Notes
- Do NOT embed production DB credentials in the repository. Use environment variables or a secrets manager.
- The skeleton uses Microsoft SQL Server (Microsoft.EntityFrameworkCore.SqlServer). Switch to Npgsql if you prefer PostgreSQL.
- This is a minimal skeleton with no real UI. Replace the placeholder MessageBox with your WinForms/WPF UI.
