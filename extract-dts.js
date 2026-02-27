const fs = require('fs');
const path = require('path');
const { Project, SyntaxKind } = require('ts-morph');

// 定位 canvaskit.d.ts 文件
const packageRoot = path.dirname(require.resolve('canvaskit-wasm'));
const dtsPath = path.join(packageRoot, 'types', 'index.d.ts');
if (!fs.existsSync(dtsPath)) {
    console.error('Cannot find index.d.ts at', dtsPath);
    process.exit(1);
}

// 创建 TypeScript 项目
const project = new Project({
    tsConfigFilePath: path.join(packageRoot, 'types', 'tsconfig.json'),
    skipAddingFilesFromTsConfig: true,
});
const sourceFile = project.addSourceFileAtPath(dtsPath);

// 存储提取的 API
const api = {
    functions: [],       // 顶层函数（如 CanvasKitInit）
    namespaces: {},      // 命名空间下的成员（如 CanvasKit 接口下的方法）
    classes: [],
    enums: [],
    interfaces: [],
    typeAliases: [],
};

// 遍历源文件中的所有声明
sourceFile.getStatements().forEach(statement => {
    // 处理接口声明（CanvasKit 本身是一个接口）
    if (statement.getKind() === SyntaxKind.InterfaceDeclaration) {
        const interfaceName = statement.getName();
        api.interfaces.push(interfaceName);

        // 如果是 CanvasKit 接口，提取其成员
        if (interfaceName === 'CanvasKit') {
            const members = statement.getMembers();
            const ns = { functions: [], properties: [] };
            members.forEach(member => {
                if (member.getKind() === SyntaxKind.MethodSignature) {
                    ns.functions.push(member.getName());
                } else if (member.getKind() === SyntaxKind.PropertySignature) {
                    ns.properties.push(member.getName());
                }
            });
            api.namespaces['CanvasKit'] = ns;
        }
    }
    // 处理类型别名
    else if (statement.getKind() === SyntaxKind.TypeAliasDeclaration) {
        api.typeAliases.push(statement.getName());
    }
    // 处理枚举
    else if (statement.getKind() === SyntaxKind.EnumDeclaration) {
        const enumName = statement.getName();
        const enumMembers = statement.getMembers().map(m => ({
            name: m.getName(),
            value: m.getValue(),
        }));
        api.enums.push({ name: enumName, members: enumMembers });
    }
    // 处理函数声明（顶层，如 CanvasKitInit）
    else if (statement.getKind() === SyntaxKind.FunctionDeclaration) {
        api.functions.push(statement.getName());
    }
    // 处理类声明（如果有）
    else if (statement.getKind() === SyntaxKind.ClassDeclaration) {
        const className = statement.getName();
        const methods = statement.getMethods().map(m => m.getName());
        api.classes.push({ name: className, methods });
    }
});

// 排序
api.functions.sort();
api.classes.sort((a, b) => a.name.localeCompare(b.name));
api.classes.forEach(c => c.methods.sort());
api.enums.sort((a, b) => a.name.localeCompare(b.name));
api.interfaces.sort();
api.typeAliases.sort();

// 输出 JSON
const outputPath = path.join(__dirname, 'canvaskit-api.json');
fs.writeFileSync(outputPath, JSON.stringify(api, null, 2), 'utf-8');
console.log('API extracted to', outputPath);
