<template>
  <div class="publish-page">
    <el-card>
      <template #header><h2>发布物品</h2></template>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="物品标题" prop="title">
          <el-input v-model="form.title" placeholder="例如：九成新 iPhone 13 Pro" />
        </el-form-item>
        <el-form-item label="物品图片" prop="images">
          <el-upload
            :action="uploadUrl" :headers="{}" :show-file-list="true" list-type="picture-card"
            :file-list="fileList" :on-success="onUploadSuccess" :on-remove="onRemove"
            :before-upload="beforeUpload" accept="image/*"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
        </el-form-item>
        <el-form-item label="详细描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="4" placeholder="描述成色、使用时长、瑕疵等" />
        </el-form-item>
        <el-form-item label="物品标签">
          <el-select
            v-model="form.tags" filterable allow-create default-first-option multiple
            placeholder="输入标签后回车，例如：数码,手机,二手"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="期望置换">
          <el-input v-model="form.expectation" placeholder="希望置换的物品描述，例如：同等价值的笔记本电脑" />
        </el-form-item>
        <el-form-item label="期望标签">
          <el-select
            v-model="form.expected_tags" filterable allow-create default-first-option multiple
            placeholder="期望置换物品的标签，用于首页匹配推荐"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="onSubmit">发布</el-button>
          <el-button @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)
const uploadUrl = '/api/uploads'

const form = reactive({
  title: '',
  description: '',
  images: [],
  tags: [],
  expectation: '',
  expected_tags: []
})

const fileList = ref([])
const rules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  description: [{ required: true, message: '请输入描述', trigger: 'blur' }]
}

function beforeUpload(file) {
  const ok = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'].includes(file.type)
  if (!ok) { ElMessage.error('仅支持 JPG/PNG/GIF/WEBP'); return false }
  if (file.size > 16 * 1024 * 1024) { ElMessage.error('图片不能超过 16MB'); return false }
  return true
}

function onUploadSuccess(res) {
  if (res.code === 0) {
    form.images.push(res.data.url)
    fileList.value.push({ name: res.data.filename, url: res.data.url })
    ElMessage.success('图片上传成功')
  }
}

function onRemove(file) {
  form.images = form.images.filter((u) => u !== file.url)
  fileList.value = fileList.value.filter((f) => f.url !== file.url)
}

async function onSubmit() {
  await formRef.value.validate()
  loading.value = true
  try {
    await request.post('/items', form)
    ElMessage.success('发布成功')
    router.push('/my-items')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.publish-page { max-width: 760px; margin: 0 auto; }
.publish-page h2 { margin: 0; }
</style>
