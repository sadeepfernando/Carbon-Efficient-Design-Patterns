# ----------------------------------------
# Run Java Patterns
# ----------------------------------------

$patterns = @(
    @{ 
        name = "Observer"
        cmd  = 'java -cp "classes;lib\gson-2.10.1.jar;lib\sqlite-jdbc-3.51.2.0.jar" observer.ObserverMain 100000 100 NUL'
    },
    @{ 
        name = "Decorator"
        cmd  = 'java -cp "classes;lib\gson-2.10.1.jar;lib\sqlite-jdbc-3.51.2.0.jar" decorator.DecoratorMain 100000 100 NUL'
    },
    @{ 
        name = "Strategy"
        cmd  = 'java -cp "classes;lib\gson-2.10.1.jar;lib\sqlite-jdbc-3.51.2.0.jar" strategy.StrategyMain 100000 100 NUL'
    }
)

$reps = 30

foreach ($p in $patterns) {

    Write-Host "======================================" -ForegroundColor Cyan
    Write-Host "Starting pattern: $($p.name)" -ForegroundColor Cyan
    Write-Host "======================================" -ForegroundColor Cyan

    # # Warm-up runs (not measured)
    # for ($w = 1; $w -le 5; $w++) {
    #     Write-Host "Warm-up $w..." -ForegroundColor DarkGray
    #     cmd /c $p.cmd | Out-Null
    # }

    # Measured runs
    for ($i = 1; $i -le $reps; $i++) {

        Write-Host "Run $i / $reps for $($p.name)" -ForegroundColor Yellow

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

Write-Host "All Java patterns completed." -ForegroundColor Green
