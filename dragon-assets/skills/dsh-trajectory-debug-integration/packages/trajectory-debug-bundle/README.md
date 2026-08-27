# dsh-trajectory-debug-bundle

Installable DSH profile bundle for the Trajectory Debug Workbench. The
`cordis.patch.yml` inserts the host provider, the RPC bridge and the browser
view into a profile's composed plugin tree.

## Install

```sh
dsh plugin --profile web add dsh-trajectory-debug-bundle
```

or from a local checkout:

```sh
dsh plugin --profile web add ./packages/trajectory-debug-bundle
```

Verify the composed tree:

```sh
dsh web --dump-config
```

## Uninstall

```sh
dsh plugin --profile web remove dsh-trajectory-debug-bundle
```

## Rows inserted

| id | package | purpose |
|---|---|---|
| `trajectory-debug-host` | `dsh-trajectory-debug-host` | engines, breakpoints, commands, projections |
| `trajectory-debug-remotes` | `dsh-trajectory-debug-remotes` | Host RPC endpoints + Client mount (M2) |
| `ui-trajectory-debug` | `dsh-client-ui-trajectory-debug` | browser views (M2) |
