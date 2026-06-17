import {
  Upload,
  MessageCircle,
  LayoutTemplate,
  Columns,
  Images,
  UserCircle,
} from "lucide-react";

const features = [
  {
    icon: Upload,
    title: "上传图片 AI 理解",
    description: "上传参考图片，AI 自动分析风格、构图与元素，精准理解你的生图意图。",
  },
  {
    icon: MessageCircle,
    title: "聊天式整理需求",
    description: "通过自然语言对话，逐步细化生图需求，告别复杂的参数配置。",
  },
  {
    icon: LayoutTemplate,
    title: "规则模板控制一致性",
    description: "设定规则模板，确保批量生成的图片在风格、色调、构图上保持一致。",
  },
  {
    icon: Columns,
    title: "多窗口工作流",
    description: "同时开启多个工作窗口，并行处理不同任务，提升创作效率。",
  },
  {
    icon: Images,
    title: "批量出图与历史回看",
    description: "一键批量生成多张图片，支持历史记录回看与对比，快速迭代。",
  },
  {
    icon: UserCircle,
    title: "个人工作空间",
    description: "专属工作空间管理项目与素材，工作进度随时保存、随时续作。",
  },
];

export default function FeatureGrid() {
  return (
    <section className="py-16 md:py-24">
      <div className="mx-auto max-w-[1200px] px-6">
        <div className="text-center mb-12 md:mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-white tracking-tight">
            核心功能
          </h2>
          <p className="mt-4 text-brand-muted text-lg max-w-2xl mx-auto">
            从上传到出图，全流程 AI 驱动，让生图更简单、更高效
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="group p-6 rounded-2xl bg-brand-surface/60 border border-white/5 hover:border-brand-accent/30 hover:bg-brand-surface/80 transition-all duration-300"
            >
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-brand-accent/20 to-brand-cyan/10 flex items-center justify-center mb-5 group-hover:from-brand-accent/30 group-hover:to-brand-cyan/20 transition-colors">
                <feature.icon
                  className="w-6 h-6 text-brand-accent"
                  strokeWidth={1.8}
                />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">
                {feature.title}
              </h3>
              <p className="text-brand-muted text-sm leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
