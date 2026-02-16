# ----------------------------------------
# Run Python Patterns 
# ----------------------------------------

$patterns = @(
    @{ name="Strategy";  cmd='python Strategy.py 100000' }
    @{ name="Observer";  cmd='python Observer.py 100000' }
    @{ name="Decorator"; cmd='python Decorator.py 100000' }
)

$reps = 30

foreach ($p in $patterns) {

    Write-Host "==========================================" -ForegroundColor Yellow
    Write-Host "Starting PYTHON Pattern: $($p.name)" -ForegroundColor Yellow
    Write-Host "=========================================="

    # ---------------------------
    # Warm-up Runs (NOT saved)
    # ---------------------------
   


    # ---------------------------
    # Measured Runs
    # ---------------------------
    for ($i = 1; $i -le $reps; $i++) {

        Write-Host "Run $i / $reps for $($p.name)" -ForegroundColor Cyan

        # Execute pattern
        # (Execution time automatically inserted into SQLite)
        cmd /c $p.cmd

        if ($i -lt $reps) {
            Write-Host "Cooling down 30 seconds..." -ForegroundColor DarkYellow
            Start-Sleep -Seconds 30
        }
    }

    Write-Host "Completed 30 runs of $($p.name)"
    Write-Host "Cooling down 3 minutes before next pattern..." -ForegroundColor Red
    Start-Sleep -Seconds 180
}

Write-Host "All Python patterns completed." -ForegroundColor Green
