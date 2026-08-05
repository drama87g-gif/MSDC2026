using Microsoft.EntityFrameworkCore;
using System;

namespace Core.Data
{
    public class MainDbContext : DbContext
    {
        public MainDbContext(DbContextOptions<MainDbContext> options) : base(options) { }

        // Example DbSet(s)
        public DbSet<Patient> Patients { get; set; }
        public DbSet<MedicalItem> MedicalItems { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);
            // configure model if needed
        }
    }
}
