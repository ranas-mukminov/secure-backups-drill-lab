# Legal and License Information

## Project License

This project is licensed under the **Apache License 2.0**. See the [LICENSE](LICENSE) file for the full text.

```
Copyright 2025 Ranas Mukminov

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

## Third-Party Tools and Their Licenses

This project **does not copy or include** any third-party code. Instead, it interfaces with the following external backup tools via their command-line interfaces (CLI) or documented APIs:

### Restic
- **License**: BSD 2-Clause License
- **Repository**: https://github.com/restic/restic
- **Usage**: Called as an external command-line tool
- **License URL**: https://github.com/restic/restic/blob/master/LICENSE

### Borg Backup
- **License**: BSD 3-Clause License
- **Repository**: https://github.com/borgbackup/borg
- **Usage**: Called as an external command-line tool
- **License URL**: https://github.com/borgbackup/borg/blob/master/LICENSE

### ZFS (OpenZFS)
- **License**: CDDL (Common Development and Distribution License)
- **Project**: https://openzfs.org/
- **Usage**: Called via system commands (zfs send, zfs receive, etc.)
- **License Information**: https://openzfs.github.io/openzfs-docs/License.html

## Compliance Statement

This project:

1. **Does NOT redistribute** any binaries or source code of restic, borg, or ZFS
2. **Does NOT copy** any code from these projects
3. **Only interacts** with these tools through their documented CLI interfaces and public APIs
4. **Expects users** to install these tools separately according to their respective licenses
5. **Maintains** full license compatibility by not incorporating any third-party code

## Python Dependencies

All Python dependencies used by this project are listed in `pyproject.toml` and are compatible with the Apache 2.0 license. Notable dependencies include:

- **Pydantic**: MIT License
- **Click**: BSD 3-Clause License
- **Prometheus Client**: Apache 2.0 License
- **APScheduler**: MIT License
- **PyYAML**: MIT License

For a complete list of dependency licenses, run:
```bash
poetry show --tree
```

## Trademarks

- "Restic" is a registered mark of the Restic project
- "Borg" refers to BorgBackup
- "ZFS" and "OpenZFS" are trademarks of their respective organizations
- "Prometheus" and "Grafana" are trademarks of their respective projects

This project is not officially affiliated with, endorsed by, or sponsored by any of these projects.

## Warranty Disclaimer

THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED. See the Apache License 2.0 for full warranty disclaimer terms.

## Security and Encryption

This project:

1. **Does NOT implement custom cryptography**
2. **Relies entirely** on the encryption provided by the underlying backup tools (restic, borg, ZFS native encryption)
3. **Recommends** users follow security best practices when configuring encryption keys and repository access

## Data Protection and Privacy

Users are responsible for:

1. **Securely storing** backup repository credentials and encryption keys
2. **Complying** with applicable data protection regulations (GDPR, etc.) when backing up personal data
3. **Testing** disaster recovery procedures in isolated lab environments
4. **Not running** destructive drill scenarios on production systems

## Contributions

By contributing to this project, you agree that your contributions will be licensed under the Apache License 2.0. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Contact

For legal inquiries or license questions, please visit: https://run-as-daemon.ru

---

*Last updated: 2025-11-19*
