const fs = require('fs');
const path = require('path');
const ts = require('typescript');

// 定位安装的 canvaskit-wasm 包中的 .d.ts 文件
const dtsPath = path.join(__dirname, 'node_modules', 'canvaskit-wasm', 'bin', 'canvaskit.d.ts');
if (!fs.existsSync(dtsPath)) {
    console.error('canvaskit.d.ts not found at', dtsPath);
    process.exit(1);
}

// 读取文件内容
const sourceCode = fs.readFileSync(dtsPath, 'utf-8');

// 创建 SourceFile
const sourceFile = ts.createSourceFile(
    'canvaskit.d.ts',
    sourceCode,
    ts.ScriptTarget.Latest,
    true
);

// 存储提取的数据
const api = {
    functions: [],      // 顶层函数
    classes: [],        // 类名及其方法
    constants: [],      // 顶层常量 (const)
    enums: {},          // 枚举名称及其成员
    interfaces: [],     // 接口（可选）
    typeAliases: []     // 类型别名（可选）
};

// 递归遍历 AST
function visit(node) {
    // 处理函数声明 (function)
    if (ts.isFunctionDeclaration(node) && node.name) {
        const name = node.name.text;
        api.functions.push(name);
    }
    // 处理变量声明 (const/let) 作为常量
    else if (ts.isVariableStatement(node)) {
        node.declarationList.declarations.forEach(decl => {
            if (ts.isVariableDeclaration(decl) && decl.name && ts.isIdentifier(decl.name)) {
                const name = decl.name.text;
                // 尝试获取初始值（如果有）
                let value = undefined;
                if (decl.initializer) {
                    if (ts.isNumericLiteral(decl.initializer)) {
                        value = Number(decl.initializer.text);
                    } else if (ts.isStringLiteral(decl.initializer)) {
                        value = decl.initializer.text;
                    } else if (ts.isIdentifier(decl.initializer) && decl.initializer.text === 'true') {
                        value = true;
                    } else if (ts.isIdentifier(decl.initializer) && decl.initializer.text === 'false') {
                        value = false;
                    }
                }
                api.constants.push({ name, value });
            }
        });
    }
    // 处理类声明
    else if (ts.isClassDeclaration(node) && node.name) {
        const className = node.name.text;
        const methods = [];

        // 遍历类的成员
        node.members.forEach(member => {
            if (ts.isMethodDeclaration(member) && member.name) {
                const methodName = member.name.getText(sourceFile);
                methods.push(methodName);
            }
            // 也可以处理属性等，这里仅提取方法
        });

        api.classes.push({ name: className, methods });
    }
    // 处理枚举声明
    else if (ts.isEnumDeclaration(node) && node.name) {
        const enumName = node.name.text;
        const members = {};
        node.members.forEach(member => {
            if (member.name) {
                const memberName = member.name.getText(sourceFile);
                // 获取枚举值（如果有初始化器）
                let value = undefined;
                if (member.initializer) {
                    if (ts.isNumericLiteral(member.initializer)) {
                        value = Number(member.initializer.text);
                    } else if (ts.isIdentifier(member.initializer)) {
                        // 可能是引用其他枚举成员，这里简单处理
                        value = member.initializer.text;
                    }
                }
                members[memberName] = value;
            }
        });
        api.enums[enumName] = members;
    }
    // 处理接口声明
    else if (ts.isInterfaceDeclaration(node) && node.name) {
        const interfaceName = node.name.text;
        api.interfaces.push(interfaceName);
    }
    // 处理类型别名
    else if (ts.isTypeAliasDeclaration(node) && node.name) {
        const aliasName = node.name.text;
        api.typeAliases.push(aliasName);
    }

    // 继续遍历子节点
    ts.forEachChild(node, visit);
}

// 开始遍历
visit(sourceFile);

// 排序和整理
api.functions.sort();
api.classes.sort((a, b) => a.name.localeCompare(b.name));
api.classes.forEach(cls => cls.methods.sort());
api.constants.sort((a, b) => a.name.localeCompare(b.name));
api.enums = Object.fromEntries(Object.entries(api.enums).sort(([a], [b]) => a.localeCompare(b)));

// 输出为 JSON 文件
const outputPath = path.join(__dirname, 'canvaskit-api.json');
fs.writeFileSync(outputPath, JSON.stringify(api, null, 2), 'utf-8');
console.log(`API extracted to ${outputPath}`);
