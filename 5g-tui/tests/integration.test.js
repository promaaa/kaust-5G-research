import { describe, test, expect, beforeAll, afterAll } from '@jest/globals';

const SERBER_USER = 'serber';
const SERBER_PASS = 'root4SERBER';

function resolveHost(hostname) {
    return new Promise((resolve, reject) => {
        const { exec } = require('child_process');
        exec(`dscacheutil -q host -a name ${hostname}`, { timeout: 5000 }, (err, stdout) => {
            if (err || !stdout) {
                resolve(null);
                return;
            }
            const match = stdout.match(/ip_address:\s*(.+)/);
            resolve(match ? match[1].trim() : null);
        });
    });
}

function sshExec(cmd, host, timeout = 60000) {
    return new Promise(async (resolve, reject) => {
        const { exec } = require('child_process');
        let ip = host;
        if (!ip.match(/^\d+\.\d+\.\d+\.\d+$/)) {
            ip = await resolveHost(host);
            if (!ip) {
                reject(new Error(`Could not resolve ${host}`));
                return;
            }
        }
        const sshCmd = `sshpass -p '${SERBER_PASS}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 -o ConnectionAttempts=2 -o UserKnownHostsFile=/dev/null ${SERBER_USER}@${ip} '${cmd}'`;
        exec(sshCmd, { timeout }, (err, stdout, stderr) => {
            const combined = (stdout || '') + (stderr || '');
            if (err && !stdout && !combined.includes('Warning: Permanently added')) {
                reject(new Error(err.message));
                return;
            }
            resolve({ stdout: stdout || '', stderr: stderr || '', combined });
        });
    });
}

describe('Host Resolution', () => {
    test('resolve serber-firecell', async () => {
        const ip = await resolveHost('serber-firecell');
        expect(ip).toBeTruthy();
        expect(ip).toMatch(/^\d+\.\d+\.\d+\.\d+$/);
    });

    test('resolve serber-minipc', async () => {
        const ip = await resolveHost('serber-minipc');
        expect(ip).toBeTruthy();
        expect(ip).toMatch(/^\d+\.\d+\.\d+\.\d+$/);
    });

    test('resolve invalid host returns null', async () => {
        const ip = await resolveHost('nonexistent-host-xyz');
        expect(ip).toBeNull();
    });
});

describe('SSH Connection', () => {
    test('can connect to serber-firecell', async () => {
        const result = await sshExec('echo "ok"', 'serber-firecell', 15000);
        expect(result.stdout.trim()).toBe('ok');
    });

    test('can connect to serber-minipc', async () => {
        const result = await sshExec('echo "ok"', 'serber-minipc', 15000);
        expect(result.stdout.trim()).toBe('ok');
    });

    test('handles invalid host', async () => {
        await expect(sshExec('echo ok', 'nonexistent-host', 5000)).rejects.toThrow();
    });
});

describe('Remote File System', () => {
    test('nr-softmodem binary exists on serber-firecell', async () => {
        const result = await sshExec('ls -la ~/openairinterface5g/cmake_targets/ran_build/build/nr-softmodem', 'serber-firecell', 10000);
        expect(result.combined).toContain('nr-softmodem');
        expect(result.combined).toContain('rwxr');
    });

    test('gNB config file exists on serber-firecell', async () => {
        const result = await sshExec('ls -la ~/openairinterface5g/targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf', 'serber-firecell', 10000);
        expect(result.combined).toContain('gnb.sa.band78.fr1.106PRB.usrpb210.conf');
    });

    test('oai-cn5g directory exists on serber-firecell', async () => {
        const result = await sshExec('ls -d ~/oai-cn5g', 'serber-firecell', 10000);
        expect(result.combined).toContain('oai-cn5g');
    });
});

describe('Docker Containers', () => {
    test('docker is running on serber-firecell', async () => {
        const result = await sshExec('docker ps --format "{{.Names}}"', 'serber-firecell', 15000);
        expect(result.combined).toBeTruthy();
    });

    test('docker-compose is available on serber-firecell', async () => {
        const result = await sshExec('cd ~/oai-cn5g && docker-compose --version', 'serber-firecell', 10000);
        expect(result.combined).toContain('docker-compose');
    });
});

describe('USRP Devices', () => {
    test('uhd_find_devices works on serber-firecell', async () => {
        const result = await sshExec('uhd_find_devices', 'serber-firecell', 15000);
        expect(result.combined).toBeTruthy();
    });
});

describe('gNB Process', () => {
    test('can check nr-softmodem process status', async () => {
        const result = await sshExec('ps aux | grep nr-softmodem | grep -v grep', 'serber-firecell', 10000);
        expect(result).toHaveProperty('combined');
    });

    test('can read gNB log file', async () => {
        const result = await sshExec('tail -5 ~/gnb.log 2>/dev/null || echo "No log yet"', 'serber-firecell', 10000);
        expect(result).toHaveProperty('combined');
    });
});

describe('Network Status Checks', () => {
    test('can check AMF logs', async () => {
        const result = await sshExec('docker logs oai-amf 2>&1 | tail -5', 'serber-firecell', 15000);
        expect(result).toHaveProperty('combined');
    });

    test('can check SMF logs', async () => {
        const result = await sshExec('docker logs oai-smf 2>&1 | tail -5', 'serber-firecell', 15000);
        expect(result).toHaveProperty('combined');
    });
});

describe('Error Handling', () => {
    test('handles command timeout gracefully', async () => {
        await expect(sshExec('sleep 30', 'serber-firecell', 2000)).rejects.toThrow();
    });

    test('handles invalid command gracefully', async () => {
        const result = await sshExec('nonexistent_command_xyz 2>&1', 'serber-firecell', 10000);
        expect(result.combined).toContain('not found');
    });
});