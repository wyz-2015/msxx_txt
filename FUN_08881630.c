
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

typedef unsigned int uint;

/* 在追踪过程中得知：
 * TXT文件很可能先被一口气读进了一个buffer中，辗转一两个小函数后来到了这里。
 * 在这里，TXT文件中的元数据信息被单独取出，像表一样地写进了另一个buffer(*puVar3)中。
 */
void FUN_08881630(uint* param_1, undefined4 param_2, int param_3, uint param_4) // 以下称*param_1为“*inBuffer”，*puVar3为“*outBuffer”
{
	uint* puVar1;
	uint uVar2;
	uint* puVar3;
	uint uVar4;

	if (param_1 != (uint*)0x0) { // param_1 != NULL
		uVar4 = 0;	     // for (uVar4 = 0; uVar4 < 6; uVar += 1) { ... }
		puVar3 = (uint*)&DAT_08b0e7cc;
		do {
			uVar2 = *param_1; // inBuffer[0]
			*puVar3 = uVar2;
			param_1 = param_1 + 1;					 // buffer += 1;
			puVar1 = FUN_08861ec8(uVar2 * 0xc, 8, param_3, param_4); // FUN_08861ec8()类似malloc()，应该是malloc()再memalign() ？
			puVar3[1] = (uint)puVar1;

			param_4 = 0; // 用作计数器的变量
			if (*puVar3 != 0) {
				param_3 = 0;
				do {
					puVar1 = (uint*)(puVar3[1] + param_3);
					*puVar1 = *param_1; // inBuffer[1]
					param_4 = param_4 + 1;
					param_3 = param_3 + 0xc;
					puVar1[1] = param_1[1]; // inBuffer[2]
					puVar1[2] = (uint)(param_1 + 2);
					param_1 = (uint*)((int)(param_1 + 2) + puVar1[1] * 2); // 指针原指向(buffer + 1)，先inBuffer += 2，跳过两个uint32_t数(已被读取),
											       // 把目前的地址当作纯数字(或转为void*型)，inBuffer += 2 * 字数，指针得以再往后跳(字数 * sizeof(UChar))Byte
											       // 应该是因为PSP的用户内存空间地址范围够小，地址值强制转换到(int)是可行的
				} while (param_4 < *puVar3);
			}
			uVar4 = uVar4 + 1; // uVar4 += 1;
			puVar3 = puVar3 + 2;
		} while (uVar4 < 6); // 写死6块blockSet，可还行，有点抽象……也不排除是宏定义
		DAT_088eae2c = 10;
		_DAT_08b0c7c8 = 0;
	}
	return;
}

/* 可注意到，inBuffer的读取是：(0, 1, 2的代号取自上方的inBuffer[n]中的“n”)
 * [0, 1, 2, 1, 2, ..., 0, 1, 2, 1, 2, ...]
 * 推知TXT的结构是：
 * [
 * 	[0,
 *	 	[1, 2, [str]], // 0, 1, 2代表uint32_t数
 * 		[1, 2, [str]], // str代表utf16le字符串，每个字符串以0x0000结尾。[str]代表字符串列表，一个block里可以有多个字符串
 * 		...
 * 	],
 *
 * 	[0,
 *	 	[1, 2, [str]],
 * 		[1, 2, [str]],
 * 		...
 * 	],
 *
 * 	...
 * ]
 */
