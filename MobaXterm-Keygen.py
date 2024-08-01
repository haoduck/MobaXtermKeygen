#/usr/bin/env python3
'''
Author: Double Sine
License: GPLv3
'''
import os, sys, zipfile

VariantBase64Table = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
VariantBase64Dict = { i : VariantBase64Table[i] for i in range(len(VariantBase64Table)) }
VariantBase64ReverseDict = { VariantBase64Table[i] : i for i in range(len(VariantBase64Table)) }

def VariantBase64Encode(bs: bytes):
    result = b''
    blocks_count, left_bytes = divmod(len(bs), 3)

    for i in range(blocks_count):
        coding_int = int.from_bytes(bs[3 * i:3 * i + 3], 'little')
        block = VariantBase64Dict[coding_int & 0x3f]
        block += VariantBase64Dict[(coding_int >> 6) & 0x3f]
        block += VariantBase64Dict[(coding_int >> 12) & 0x3f]
        block += VariantBase64Dict[(coding_int >> 18) & 0x3f]
        result += block.encode()

    if left_bytes == 0:
        return result
    elif left_bytes == 1:
        coding_int = int.from_bytes(bs[3 * blocks_count:], 'little')
        block = VariantBase64Dict[coding_int & 0x3f]
        block += VariantBase64Dict[(coding_int >> 6) & 0x3f]
        result += block.encode()
        return result
    else:
        coding_int = int.from_bytes(bs[3 * blocks_count:], 'little')
        block = VariantBase64Dict[coding_int & 0x3f]
        block += VariantBase64Dict[(coding_int >> 6) & 0x3f]
        block += VariantBase64Dict[(coding_int >> 12) & 0x3f]
        result += block.encode()
        return result

def VariantBase64Decode(s: str):
    result = b''
    blocks_count, left_bytes = divmod(len(s), 4)

    for i in range(blocks_count):
        block = VariantBase64ReverseDict[s[4 * i]]
        block += VariantBase64ReverseDict[s[4 * i + 1]] << 6
        block += VariantBase64ReverseDict[s[4 * i + 2]] << 12
        block += VariantBase64ReverseDict[s[4 * i + 3]] << 18
        result += block.to_bytes(3, 'little')

    if left_bytes == 0:
        return result
    elif left_bytes == 2:
        block = VariantBase64ReverseDict[s[4 * blocks_count]]
        block += VariantBase64ReverseDict[s[4 * blocks_count + 1]] << 6
        result += block.to_bytes(1, 'little')
        return result
    elif left_bytes == 3:
        block = VariantBase64ReverseDict[s[4 * blocks_count]]
        block += VariantBase64ReverseDict[s[4 * blocks_count + 1]] << 6
        block += VariantBase64ReverseDict[s[4 * blocks_count + 2]] << 12
        result += block.to_bytes(2, 'little')
        return result
    else:
        raise ValueError('编码无效。')

def EncryptBytes(key: int, bs: bytes):
    result = bytearray()
    for i in range(len(bs)):
        result.append(bs[i] ^ ((key >> 8) & 0xff))
        key = result[-1] & key | 0x482D
    return bytes(result)

def DecryptBytes(key: int, bs: bytes):
    result = bytearray()
    for i in range(len(bs)):
        result.append(bs[i] ^ ((key >> 8) & 0xff))
        key = bs[i] & key | 0x482D
    return bytes(result)

class LicenseType:
    Professional = 1
    Educational = 3
    Persional = 4

def GenerateLicense(Type: LicenseType, Count: int, UserName: str, MajorVersion: int, MinorVersion):
    assert(Count >= 0)
    LicenseString = '%d#%s|%d%d#%d#%d3%d6%d#%d#%d#%d#' % (Type, 
                                                          UserName, MajorVersion, MinorVersion, 
                                                          Count, 
                                                          MajorVersion, MinorVersion, MinorVersion,
                                                          0,    # 未知
                                                          0,    # No Games标志。0表示“NoGames = false”。但它不起作用。
                                                          0)    # No Plugins标志。0表示“NoPlugins = false”。但它不起作用。
    EncodedLicenseString = VariantBase64Encode(EncryptBytes(0x787, LicenseString.encode())).decode()
    with zipfile.ZipFile('Custom.mxtpro', 'w') as f:
        f.writestr('Pro.key', data=EncodedLicenseString)

def help():
    print('用法:')
    print('    MobaXterm-Keygen.py <用户名> <版本号> <授权数量>')
    print()
    print('    <用户名>:        授权的用户名 (默认: username)')
    print('    <版本号>:        MobaXterm 的版本号 (默认: 24.2)')
    print('    <授权数量>:      授权的数量 (默认: 99)')
    print()

if __name__ == '__main__':
    if len(sys.argv) != 4:
        UserName = input("请输入用户名 (默认: username): ") or "username"
        Version = input("请输入版本号 (例如: 24.2, 默认: 24.2): ") or "24.2"
        Count = input("请输入授权数量 (默认: 99): ") or "99"
        MajorVersion, MinorVersion = Version.split('.')[0:2]
        MajorVersion = int(MajorVersion)
        MinorVersion = int(MinorVersion)
        Count = int(Count)
    else:
        UserName = sys.argv[1]
        MajorVersion, MinorVersion = sys.argv[2].split('.')[0:2]
        MajorVersion = int(MajorVersion)
        MinorVersion = int(MinorVersion)
        Count = int(sys.argv[3])

    GenerateLicense(LicenseType.Professional, 
                    Count,
                    UserName, 
                    MajorVersion, 
                    MinorVersion)
    print('[*] 成功!')
    print('[*] 文件已生成: %s' % os.path.join(os.getcwd(), 'Custom.mxtpro'))
    print('[*] 请将新生成的文件移动或复制到 MobaXterm 的安装路径中.')
    print()
    print('[*] 按任意键退出.')
    print()
    input()